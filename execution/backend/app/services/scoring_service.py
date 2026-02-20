"""Service for orchestrating company scoring."""

from datetime import datetime
from typing import Optional, Union

from sqlalchemy import select
from sqlalchemy.orm import Session

from fastapi import BackgroundTasks

from app.models.company import Company, Score
from app.models.enums import AIReadinessCategory
from app.services.scrapers.orchestrator import ScraperOrchestrator
from app.services.scrapers.ats_detector import ATSDetector
from app.services.scoring.calculator import ScoreCalculator, SignalData
from app.services.scoring.model import get_category_label
from app.schemas.scores import ScoreResponse, SignalResponse, ComponentScoresResponse, ScoringStatusResponse
from bs4 import BeautifulSoup
import asyncio
import re
from typing import Dict
from urllib.parse import urljoin, urlparse
import tldextract

# Tiered AI keyword lists for quality-weighted analysis
AI_KEYWORD_TIERS = {
    "success": {
        # Evidence of AI actually deployed/working (high value)
        "terms": [
            "ai-powered", "ai powered", "ml-driven", "ml driven",
            "ai deployment", "deployed ai", "ai in production",
            "production model", "model serving", "inference pipeline",
            "ai revenue", "ai-generated revenue",
            "automated with ai", "automated with ml",
            "ai transformation results", "roi from ai",
            "ai patent",
        ],
        "regexes": [
            r'\b\d+%.*(?:automat|efficien|improv|reduc).*\b(?:ai|ml)\b',
            r'\b(?:ai|ml)\b.*\b\d+%.*(?:automat|efficien|improv|reduc)',
            r'\b(?:launch|ship|deploy|release)(?:ed|ing)?\b.*\b(?:ai|ml)\b',
        ],
        "points_per_match": 3,
    },
    "plan": {
        # Evidence of AI strategy/investment/roadmap (medium value)
        "terms": [
            "ai strategy", "ai roadmap", "ai investment",
            "ai initiative", "ai transformation",
            "ai first", "ai-first",
            "chief ai officer", "head of ai", "vp of ai",
            "ai budget", "investing in ai", "ai partnership",
            "ai center of excellence", "ai coe",
            "ai governance", "responsible ai",
            "generative ai strategy", "genai strategy",
            "ai adoption", "ai maturity",
        ],
        "regexes": [
            r'\b(?:invest|commit|allocat|dedicat)(?:ed|ing|s)?\b.*\$?\d+.*\b(?:ai|ml|artificial intelligence)\b',
            r'\b(?:ai|ml)\b.*\b(?:pilot|poc|proof of concept|prototype)\b',
        ],
        "points_per_match": 2,
    },
    "generic": {
        # Generic AI mentions (baseline — current behavior)
        "terms": [
            "artificial intelligence", "machine learning", "deep learning",
            "nlp", "computer vision", "generative ai", "llm",
            "data science", "experimentation", "data platform",
            "ml platform", "ai agent",
        ],
        "regexes": [
            r'\bai\b',
            r'\bml\b',
        ],
        "points_per_match": 1,
    },
}

# Source types that are news/press/IR (subject to recency weighting)
NEWS_SOURCE_TYPES = {"news_article", "press_release", "investor_relations", "newsroom"}

_DATE_PATTERNS = [
    r'(\w+ \d{1,2},? \d{4})',
    r'(\d{4}-\d{2}-\d{2})',
    r'(\d{1,2}/\d{1,2}/\d{4})',
    r'(\d{1,2} \w+ \d{4})',
]
_DATE_FORMATS = [
    "%B %d, %Y", "%B %d %Y", "%b %d, %Y", "%b %d %Y",
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d %B %Y", "%d %b %Y",
]


def _estimate_recency_multiplier(text: str) -> float:
    """
    Best-effort date extraction from article text.
    Returns 1.0 for <=45 days, 0.5 for 45-90 days, 0.0 for >90 days.
    Falls back to 0.7 if no date found.
    """
    now = datetime.now()
    found_dates = []
    for pattern in _DATE_PATTERNS:
        matches = re.findall(pattern, text)
        for m in matches:
            for fmt in _DATE_FORMATS:
                try:
                    d = datetime.strptime(m.strip(), fmt)
                    if d.year >= 2020:
                        found_dates.append(d)
                except ValueError:
                    continue

    if not found_dates:
        return 0.7

    most_recent = max(found_dates)
    days_old = (now - most_recent).days

    if days_old <= 45:
        return 1.0
    elif days_old <= 90:
        return 0.5
    else:
        return 0.0


def _normalize_component_scores(raw: dict) -> dict:
    """Normalize legacy component score keys from DB data."""
    normalized = dict(raw)
    if 'ai_platform_team' in normalized and 'ai_in_it' not in normalized:
        normalized['ai_in_it'] = normalized.pop('ai_platform_team')
    elif 'ai_platform_team' in normalized:
        normalized.pop('ai_platform_team')
    return normalized


class ScoringService:
    def __init__(self, db: Session):
        self.db = db
        self.scraper = ScraperOrchestrator()
        self.calculator = ScoreCalculator()

    async def check_or_start_scoring(self, url: str, background_tasks: BackgroundTasks) -> Union[ScoreResponse, ScoringStatusResponse]:
        """
        Check if we have a recent score. If not, start background scoring.
        """
        existing_score = await self.get_latest_score(url)
        if existing_score:
            return existing_score

        # Start background task
        background_tasks.add_task(self.score_company, url)
        
        return ScoringStatusResponse(
            status="processing",
            message="Analysis started! This typically takes 2-3 minutes. Please check back later.",
            careers_url=url
        )

    async def get_latest_score(self, url: str) -> Optional[ScoreResponse]:
        """Check if we have a recent score for this URL."""
        # 1. Parse domain using tldextract for robust matching
        extracted = await asyncio.to_thread(tldextract.extract, url)
        root_domain = f"{extracted.domain}.{extracted.suffix}"
        
        # Robust Domain Matching
        # We check primarily for the root domain (google.com)
        # But also check specific input URL and legacy "www." records
        
        domains_to_check = {root_domain, f"www.{root_domain}"}

        stmt = select(Company).where(
            (Company.domain.in_(domains_to_check)) |
            (Company.careers_url == url)
        )
        companies = self.db.execute(stmt).scalars().all()
        
        # Pick best match (with scores)
        for company in companies:
            if company.scores:
                latest_score = company.scores[0] # Assumes desc order
                return ScoreResponse(
                    company_id=company.id,
                    company_name=company.name,
                    careers_url=company.careers_url,
                    score=round(latest_score.score, 1),
                    category=latest_score.category.value,
                    category_label=get_category_label(latest_score.category),
                    signals=SignalResponse(**latest_score.signals),
                    component_scores=ComponentScoresResponse(**_normalize_component_scores(latest_score.component_scores)),
                    evidence=latest_score.evidence,
                    sources=[{"url": s.url, "source_type": s.source_type} for s in company.sources],
                    scored_at=latest_score.created_at
                )
        return None

    async def score_company(self, url: str, job_id: str | None = None):
        """
        Background Task: Score a company.
        Persistence-only, no return value expected by API caller.
        """
        from app.services.scoring_jobs import update_job
        # 1. Parse domain/name using tldextract
        # This handles subdomains (xyz.google.com -> google.com) and paths (google.com/jobs -> google.com)
        # and complex TLDs (yahoo.co.uk -> yahoo.co.uk)
        # Run blocking tldextract in thread (it may fetch updates)
        extracted = await asyncio.to_thread(tldextract.extract, url)
        # Reconstruct the root domain (domain + suffix)
        root_domain = f"{extracted.domain}.{extracted.suffix}"
        
        # Company Name Heuristic: Cap first letter of domain part
        company_name = extracted.domain.capitalize()
        
        # Use full domain (subdomain + domain + suffix) for specific subdomain checks later if needed,
        # but the identity is tied to root_domain
        full_domain = f"{extracted.subdomain}.{extracted.domain}.{extracted.suffix}" if extracted.subdomain else root_domain

        # Story 4.5: Trace Logging

        # Story 4.5: Trace Logging
        trace_steps = []
        def log_trace(step: str, detail: any = None):
            entry = {"timestamp": datetime.now().isoformat(), "step": step, "detail": detail}
            trace_steps.append(entry)
            print(f"[Trace] {step}: {detail if detail else ''}")

        log_trace("Starting scoring", {"url": url, "company": company_name})

        # 2. Discovery (Run first to allow broad scraping)
        from app.services.discovery import DiscoveryService
        from app.models.company import CompanySource
        
        discovery = DiscoveryService()
        log_trace("DiscoveryService: Finding sources")
        # Run synchronous blocking search in a separate thread
        discovered_sources = await asyncio.to_thread(discovery.find_sources, company_name, root_domain)
        log_trace("DiscoveryService Results", {"count": len(discovered_sources), "sources": [s['url'] for s in discovered_sources]})
        print(f"Discovered {len(discovered_sources)} potential sources: {[s['url'] for s in discovered_sources]}")

        # Story 5-7: Load Verified User/Admin Sources
        from app.models.enums import VerificationStatus
        
        # We need to find the company by domain to get its sources
        stmt = select(Company).where(Company.domain == root_domain)
        existing_company = self.db.execute(stmt).scalars().first()
        
        if existing_company:
            # Load verified sources
            saved_sources = self.db.execute(
                select(CompanySource).where(
                    CompanySource.company_id == existing_company.id,
                    CompanySource.verification_status == VerificationStatus.VERIFIED,
                    CompanySource.is_active == True
                )
            ).scalars().all()
            
            if saved_sources:
                log_trace("Loaded verified sources from DB", {"count": len(saved_sources)})
                print(f"Loaded {len(saved_sources)} verified sources from DB")
                
                for s in saved_sources:
                     # Add to discovered_sources if not present
                     if not any(d['url'] == s.url for d in discovered_sources):
                          discovered_sources.append({"url": s.url, "type": s.source_type})

        # 3. Scrape Main URL
        try:
            scrape_result = await self.scraper.scrape(url)
            
            # Collect text segments for analysis
            text_segments = {}
            
            if not scrape_result.success:
                # ... existing error handling ...
                print(f"Scrape failed for {url}")
            else:
                text_segments["homepage"] = scrape_result.extracted_text or ""
                
                # Story 4.3: Detect ATS Links (Greenhouse, Lever, etc.)
                ats_links = discovery.extract_ats_links(scrape_result.raw_html)
                if ats_links:
                    print(f"Found {len(ats_links)} ATS links (High Confidence): {ats_links}")
                    for link in ats_links:
                        # Add to discovered sources for deep scraping
                        # We use 'job_posting_verified' type to trigger high weighting
                        discovered_sources.append({"url": link, "type": "job_posting_verified"})

            # 4. Scrape Discovered Sources (Satellite Strategy)
            if discovered_sources:
                from app.utils.source_detection import detect_source_type
                print(f"Deep scraping {len(discovered_sources)} satellite sources...")
                tasks = [self.scraper.scrape(src["url"]) for src in discovered_sources]
                satellite_results = await asyncio.gather(*tasks)

                for i, res in enumerate(satellite_results):
                    if res.success and res.extracted_text:
                        source_type = discovered_sources[i]['type']
                        # Re-classify ATS/job links by department using actual content.
                        # A PM role on Greenhouse should be product_role, not job_posting_verified.
                        if source_type in ("job_posting_verified", "job_posting"):
                            source_type = detect_source_type(discovered_sources[i]['url'], res.extracted_text)
                        if source_type in text_segments:
                             text_segments[source_type] += "\n" + res.extracted_text
                        else:
                             text_segments[source_type] = res.extracted_text

            # 5. Deep Scrape (Internal Job Links)
            deep_links = self._find_job_links(scrape_result.raw_html if scrape_result.success else "", url)
            log_trace("Deep Scrape: Finding job links", {"count": len(deep_links)})
            
            # Story 4.4: Scan for high-signal subdomains (ai.*, research.*)
            # We do this asynchronously or simply just before deep scraping
            print("Scanning for high-signal subdomains...")
            log_trace("Scanning subdomains")
            subdomains = discovery.discover_subdomains(company_name, root_domain)
            if subdomains:
                log_trace(f"Found {len(subdomains)} subdomains", [s['url'] for s in subdomains])
                print(f"Found {len(subdomains)} subdomains: {[s['url'] for s in subdomains]}")
                discovered_sources.extend(subdomains)
                # We need to scrape them now if we haven't already
                # (Logic above scraped discovered_sources before this... we should move this up or re-trigger)
                
                # Re-trigger scraping for NEWLY found subdomains
                # Filter out ones we already scraped (unlikely as we just found them)
                new_tasks = [self.scraper.scrape(src["url"]) for src in subdomains]
                new_results = await asyncio.gather(*new_tasks)
                
                for i, res in enumerate(new_results):
                    if res.success and res.extracted_text:
                        src_type = subdomains[i]['type']
                        if src_type in text_segments:
                             text_segments[src_type] += "\n" + res.extracted_text
                        else:
                             text_segments[src_type] = res.extracted_text

            # Story 4.3 AC2: Emergency Crawl — if discovery failed and we have few job links,
            # do a deeper crawl to find more job pages
            if discovery.search_failed and len(deep_links) < 3 and scrape_result.success:
                print("Emergency Crawl: Discovery failed, expanding job link search...")
                emergency_links = await self._emergency_crawl(url, scrape_result.raw_html, depth=2)
                # Merge, dedup
                existing = set(deep_links)
                for link in emergency_links:
                    if link not in existing:
                        deep_links.append(link)
                        existing.add(link)
                print(f"Emergency Crawl found {len(emergency_links)} additional links (total: {len(deep_links)})")

            if deep_links:
                from app.utils.source_detection import detect_source_type
                scrape_count = min(len(deep_links), 5)  # Scrape up to 5 in emergency mode
                print(f"Found {len(deep_links)} potential job links. Deep scraping top {scrape_count}...")
                tasks = [self.scraper.scrape(link) for link in deep_links[:scrape_count]]
                deep_results = await asyncio.gather(*tasks)

                for i, dr in enumerate(deep_results):
                        if dr.success and dr.extracted_text:
                            source_type = detect_source_type(deep_links[i], dr.extracted_text)
                            if source_type in text_segments:
                                text_segments[source_type] += "\n" + dr.extracted_text
                            else:
                                text_segments[source_type] = dr.extracted_text
            
            # 5b. Inject Google search snippets as a signal source.
            # Discovery captures .title + .description from every Google query.
            # These contain hiring signals, salary info, AI policy mentions, etc.
            # that may not appear on the pages we scrape.
            if discovery.collected_snippets:
                snippet_text = "\n".join(discovery.collected_snippets)
                text_segments["google_snippets"] = snippet_text
                log_trace("Google snippets collected", {
                    "count": len(discovery.collected_snippets),
                    "chars": len(snippet_text),
                })
                print(f"Collected {len(discovery.collected_snippets)} Google search snippets ({len(snippet_text)} chars)")

            # 6. Extract & Calculate
            signals = self._extract_signals_heuristically(text_segments)

            score_result = self.calculator.calculate(company_name, signals)
            
            score_data = {
                "score": score_result.score,
                "category": score_result.category,
                "signals": score_result.signals.to_dict(),
                "component_scores": score_result.component_scores,
                "evidence": score_result.evidence
            }

            # 7. Persist
            if score_data:
                # We need to access the db session. Reusing self.db.
                company = self._get_or_create_company(company_name, root_domain, url)
                
                # Story 4.5: Save trace
                log_trace("Scoring Complete", {"score": score_data["score"]})
                company.discovery_trace = {"steps": trace_steps}
                self.db.add(company)
                
                # Save sources
                for src in discovered_sources:
                    # Check duplicate? simplistic check
                    exists = False
                    for existing in company.sources:
                        if existing.url == src["url"]:
                            exists = True
                            break
                    
                    if not exists:
                        new_source = CompanySource(
                            company_id=company.id,
                            url=src["url"],
                            source_type=src["type"]
                        )
                        self.db.add(new_source)
                
                score_record = Score(
                    company_id=company.id,
                    score=score_data["score"],
                    category=score_data["category"],
                    signals=score_data["signals"],
                    component_scores=score_data["component_scores"],
                    evidence=score_data["evidence"]
                )
                self.db.add(score_record)
                self.db.commit()
                print(f"Successfully scored {company_name}")

                if job_id:
                    update_job(job_id, "completed", company_name=company_name)

        except Exception as e:
            print(f"Error in background scoring task for {url}: {e}", flush=True)
            if job_id:
                update_job(job_id, "failed", error=str(e))
            try:
                with open("debug_scoring.txt", "a") as f:
                    f.write(f"Error for {url}: {e}\n")
            except:
                pass


    def _get_or_create_company(self, name: str, domain: str, url: str) -> Company:
        # Use tldextract to ensure we matched the root domain regardless of what was passed
        extracted = tldextract.extract(url)
        root_domain = f"{extracted.domain}.{extracted.suffix}"
        
        # Normalize URL to root domain (not subdomain)
        # Subdomains like careers.google.com go in careers_url, not url
        root_url = f"https://{root_domain}"
        
        # Story 4-8: Check alias table first
        from app.models.company import CompanyDomainAlias
        
        alias = self.db.execute(
            select(CompanyDomainAlias).where(CompanyDomainAlias.alias_domain == root_domain)
        ).scalar_one_or_none()
        
        if alias:
            # Found an alias - return the parent company
            company = self.db.execute(
                select(Company).where(Company.id == alias.company_id)
            ).scalar_one_or_none()
            if company:
                return company
        
        # Prioritize matching by Domain (most stable), then name/url
        stmt = select(Company).where(
            (Company.domain == root_domain) | 
            (Company.name == name)
        )
        # Fix: handle duplicates gracefully (pick first)
        results = self.db.execute(stmt).scalars().all()
        company = results[0] if results else None
        
        if not company:
            company = Company(name=name, domain=root_domain, url=root_url, careers_url=url)
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
        else:
            # Update URLs if missing
            if not company.careers_url:
                company.careers_url = url
            
            # Ensure domain is normalized in DB if it was old/messy
            if company.domain != root_domain:
                company.domain = root_domain
            
            # Ensure url is root domain, not subdomain
            if company.url != root_url:
                company.url = root_url
            
            self.db.add(company) # persist updates
            self.db.commit()
            
        return company

    def _extract_signals_heuristically(self, text_segments: Dict[str, str]) -> SignalData:
        """
        Extract signals from segmented text sources to allow weighting and attribution.
        """
        
        # Initialize tracking
        sources_map = {
            "ai_keywords": [],
            "tool_stack": [],
            "agentic_signals": [],
            "non_eng_ai_roles": []
        }
        
        eng_keyword_sources = {"github", "engineering_blog", "job_posting", "job_posting_verified", "ats_link", "careers_fallback", "subdomain_engineering", "subdomain_dev"}
        non_eng_keywords = 0
        eng_ai_keywords = 0
        ai_success_points = 0
        ai_plan_points = 0
        ai_generic_points = 0
        tools_found = set()
        agentic_count = 0
        non_eng_score = 0
        has_platform_team = False

        # Comprehensive AI/ML tool detection — exact-match terms grouped by category.
        # Defined here so both analyze_segment and weighted-tool calculation can use it.
        known_tools = [
            # Cloud ML Platforms
            "sagemaker", "vertex ai", "bedrock", "azure ml", "azure openai",
            "azure cognitive", "google cloud ai", "amazon q",
            # Frameworks & Libraries
            "pytorch", "tensorflow", "jax", "keras", "scikit-learn", "sklearn",
            "xgboost", "lightgbm", "catboost", "onnx", "triton inference",
            # LLM Providers & APIs
            "openai", "anthropic", "cohere", "mistral", "groq",
            "together ai", "fireworks ai", "replicate", "ollama", "perplexity",
            # LLM Frameworks & Orchestration
            "langchain", "langgraph", "langsmith", "llamaindex", "llama index",
            "semantic kernel", "haystack", "dspy", "crewai", "autogen",
            "model context protocol",
            # Model Hubs & Pretrained
            "huggingface", "hugging face", "transformers",
            # MLOps & Experiment Tracking
            "mlflow", "kubeflow", "wandb", "weights and biases", "weights & biases",
            "neptune", "dvc", "dagshub", "prefect", "airflow",
            "ray", "anyscale", "metaflow",
            # Vector / AI Databases
            "pinecone", "weaviate", "milvus", "qdrant", "chroma", "chromadb",
            "pgvector", "faiss",
            # Infrastructure & Cloud
            "kubernetes", "aws", "gcp", "azure", "databricks", "snowflake",
            "spark", "delta lake", "lakehouse",
            # AI Dev Tools & Coding Assistants
            "copilot", "cursor", "v0", "replit", "tabnine", "codeium",
            "windsurf", "amazon codewhisperer",
            # Specific Models & Products
            "claude", "gemini", "llama", "stable diffusion",
            "dall-e", "midjourney", "whisper",
            # Observability & Evaluation
            "langfuse", "helicone", "arize", "whylabs", "deepchecks",
            # Code & Repo Hosting
            "github",
        ]
        known_tools_set = set(known_tools)

        # Regex patterns for versioned tool names (e.g., "GPT-4o", "Claude 3.5")
        _tool_regexes = [
            (r'\bgpt-?\d', "openai"),          # GPT-4, GPT-3.5, GPT4o
            (r'\bclaude[ -]?\d', "anthropic"),  # Claude 3, Claude-3.5
            (r'\bgemini[ -]?\d', "gemini"),     # Gemini 1.5, Gemini-Pro
            (r'\bllama[ -]?\d', "llama"),       # Llama 2, Llama-3
            (r'\bmistral[ -]?\d', "mistral"),   # Mistral 7B, Mistral-Large
            (r'\bstable diffusion', "stable diffusion"),
            (r'\bdall-?e', "dall-e"),
        ]

        # Helper to analyze a segment
        def analyze_segment(source_type: str, text: str):
            nonlocal non_eng_keywords, eng_ai_keywords, agentic_count, non_eng_score, has_platform_team
            nonlocal ai_success_points, ai_plan_points, ai_generic_points
            text_lower = text.lower()

            # 1. AI Keywords — Tiered Analysis
            seg_success = 0
            seg_plan = 0
            seg_generic = 0

            for tier_name, tier_config in AI_KEYWORD_TIERS.items():
                term_count = sum(text_lower.count(term) for term in tier_config["terms"])
                regex_count = sum(len(re.findall(pat, text_lower)) for pat in tier_config.get("regexes", []))
                tier_points = (term_count + regex_count) * tier_config["points_per_match"]

                if tier_name == "success":
                    seg_success += tier_points
                elif tier_name == "plan":
                    seg_plan += tier_points
                else:
                    seg_generic += tier_points

            # Recency multiplier for news-type sources
            if source_type in NEWS_SOURCE_TYPES:
                multiplier = _estimate_recency_multiplier(text_lower)
                seg_success = int(seg_success * multiplier)
                seg_plan = int(seg_plan * multiplier)
                seg_generic = int(seg_generic * multiplier)

            segment_keywords = seg_success + seg_plan + seg_generic
            if segment_keywords > 0:
                sources_map["ai_keywords"].append(source_type)

            # Route keywords to engineering or non-engineering bucket
            if source_type in eng_keyword_sources:
                eng_ai_keywords += segment_keywords
            else:
                non_eng_keywords += segment_keywords

            # Accumulate tier totals
            ai_success_points += seg_success
            ai_plan_points += seg_plan
            ai_generic_points += seg_generic
                
            # 2. Tool Stack Detection
            # Uses known_tools and _tool_regexes defined in parent scope.

            # Exact-match detection
            for tool in known_tools:
                if tool in text_lower:
                    if tool not in tools_found:
                        tools_found.add(tool)
                        sources_map["tool_stack"].append(source_type)

            # Regex-based detection for versioned tool names
            for pattern, canonical_name in _tool_regexes:
                if canonical_name not in tools_found and re.search(pattern, text_lower):
                    tools_found.add(canonical_name)
                    sources_map["tool_stack"].append(source_type)

            # 3. Agentic Signals
            # Covers both infrastructure-level (chaos engineering, self-healing) and
            # product-level (AI-powered automation, workflow, AI assistant) agentic patterns.
            infra_agentic_terms = ["autonomous", "chaos monkey", "spinnaker", "self-healing", "chaos engineering"]
            product_agentic_terms = ["ai-powered", "ai powered", "ai assistant", "ai copilot", "automate", "automation", "automated workflow"]
            segment_agentic = sum(text_lower.count(t) for t in infra_agentic_terms)
            segment_agentic += sum(text_lower.count(t) for t in product_agentic_terms)
            # "agent" counted separately — common in both infra and product contexts
            segment_agentic += text_lower.count("agent")

            # Boost if context implies orchestration or AI-friendly documentation
            if any(t in text_lower for t in [
                "langchain", "autogen", "agentic", "orchestration",
                "llm-ready", "llm ready", "ai-friendly documentation",
                "agent-friendly", "machine-readable documentation",
                "ai-optimized documentation", "llm-friendly",
                "ai agent documentation", "documentation for ai",
                "model context protocol", "mcp server",
            ]):
                segment_agentic += 2
                
            agentic_count += segment_agentic
            if segment_agentic > 0:
                 sources_map["agentic_signals"].append(source_type)

            # 4. Non-Engineering AI Roles — Middle Management Thesis
            # Core hypothesis: middle management roles with heavy communication,
            # review, and reporting responsibilities (legal, compliance, PM, program
            # management, finance) should show AI competency as a baseline expectation
            # at AI-ready companies. No free points for just finding the role —
            # points come from AI appearing as a SKILL REQUIREMENT in the JD.
            non_eng_role_types = [
                "product_role", "marketing_role", "legal_role",
                "operations_role", "design_role", "finance_role",
                "hr_role", "sales_role",
            ]
            if source_type in non_eng_role_types or source_type == "careers_ai_keyword_hit":
                # Tier 1: AI as competency/skill requirement (strong signal)
                # Language that says "you will USE AI" not just "we talk about AI"
                ai_competency_terms = [
                    "proficiency with ai", "experience with ai", "familiarity with ai",
                    "ai tools", "ai-assisted", "ai-augmented", "leverage ai",
                    "prompt engineering", "ai literacy", "build prototypes",
                    "use ai to", "using ai", "work with ai", "ai fluency",
                    "llm", "copilot", "generative ai", "genai",
                    "ai-powered workflow", "ai-driven", "ai skills",
                    "chatgpt", "claude", "gemini",
                ]
                # Tier 2: AI mentioned in context (weaker signal)
                # The JD references AI but not as a direct skill expectation
                ai_mentioned_terms = [
                    "artificial intelligence", "machine learning",
                    "automation", "data-driven", "predictive",
                    "agent", "orchestration", "nlp",
                ]

                has_competency = any(k in text_lower for k in ai_competency_terms)
                has_mention = any(k in text_lower for k in ai_mentioned_terms)

                if has_competency:
                    # Strong: JD expects AI competency as baseline
                    non_eng_score += 7
                    sources_map["non_eng_ai_roles"].append(source_type)
                elif has_mention:
                    # Weak: AI is referenced but not as a skill requirement
                    non_eng_score += 2
                    sources_map["non_eng_ai_roles"].append(source_type)
                # No points if the role doesn't mention AI at all

                # Seniority boost: reward MIDDLE MANAGEMENT (manager, senior, lead)
                # over executives (VP, C-suite) — middle management is where
                # AI-as-competency shows organizational readiness
                if has_competency or has_mention:
                    mid_mgmt_terms = ["manager", "senior", "lead", "principal", "counsel", "analyst"]
                    exec_terms = ["vice president", "vp ", "chief ", "cto", "cfo", "coo", "head of", "director"]
                    is_mid_mgmt = any(t in text_lower for t in mid_mgmt_terms)
                    is_exec = any(t in text_lower for t in exec_terms)
                    if is_mid_mgmt and not is_exec:
                        non_eng_score += 3  # Middle management bonus
            
            # Conference Speaking (New Source)
            if source_type == "conference_speaking":
                # High value
                non_eng_score += 5 # Or count towards keywords/agentic?
                # User req: "conference and speaking engagements about this topic (High)"
                # We assume if we found it via search, it's about the topic.
                sources_map["non_eng_ai_roles"].append("conference") # misuse of field? Or maybe add new field?
                # Let's map it into non-eng score as "Thought Leadership"

            # Google Snippets: Non-Eng AI Role Detection
            # Snippets are short (title + description from search results) so we
            # look for co-occurrence of non-eng role titles with AI terms —
            # e.g. "Generative AI Product Manager" or "AI guidelines for legal".
            if source_type == "google_snippets":
                non_eng_role_titles = [
                    "product manager", "program manager", "project manager",
                    "legal", "counsel", "compliance", "finance", "financial",
                    "marketing", "design", "communications", "operations",
                    "hr ", "human resources", "sales",
                ]
                ai_terms_for_roles = [
                    "ai", "artificial intelligence", "machine learning",
                    "generative ai", "genai", "llm", "ml ",
                    "prompt engineering", "ai tools", "ai skills",
                ]
                # Check each sentence/snippet line for role+AI co-occurrence
                for line in text_lower.split("\n"):
                    has_role = any(r in line for r in non_eng_role_titles)
                    has_ai = any(a in line for a in ai_terms_for_roles)
                    if has_role and has_ai:
                        non_eng_score += 3
                        sources_map["non_eng_ai_roles"].append("google_snippets")
                        break  # One strong signal per snippet batch is enough

            # Platform Team
            if "platform" in text_lower and "ai" in text_lower:
                has_platform_team = True

        # Process all segments
        # To handle max-weight per tool, we need to defer tool counting
        tool_max_weights = {} # tool -> max_weight
        
        known_tools_set = set(known_tools)
        weights_map = {
             "github": 2.0,
             "engineering_blog": 1.5,
             "job_posting": 2.0, # High - verified hiring intent (Story 4.3 AC3)
             "homepage": 0.5,
             "conference_speaking": 1.0,
             "job_posting_verified": 2.0, # High (Story 4.3 ATS-detected)
             "careers_fallback": 1.5, # Medium-High (Story 4.3)
             "ats_link": 2.0,
             "subdomain_ai": 2.0, # High (Story 4.4)
             "subdomain_research": 2.0, # High
             "subdomain_engineering": 1.5,
             "subdomain_dev": 1.5,
             "subdomain_cloud": 1.5,
             "news_article": 0.75,
             "press_release": 0.75,
             "investor_relations": 1.0, # Public commitments to investors
             "newsroom": 0.75,
             "google_snippets": 0.75, # Search result titles + descriptions
             # Non-eng role types (treat like job postings for tool weighting)
             "product_role": 1.5,
             "marketing_role": 1.0,
             "legal_role": 1.0,
             "operations_role": 1.0,
             "design_role": 1.0,
             "finance_role": 1.0,
             "hr_role": 1.0,
             "sales_role": 1.0,
             "careers_ai_keyword_hit": 1.5, # Found via AI keyword search on careers
        }

        for src_type, txt in text_segments.items():
            analyze_segment(src_type, txt)
            
            # Separate pass for efficient max-weight calc
            txt_lower = txt.lower()
            w = weights_map.get(src_type, 0.5)
            for tool in known_tools_set:
                if tool in txt_lower:
                    current_max = tool_max_weights.get(tool, 0.0)
                    if w > current_max:
                        tool_max_weights[tool] = w
            # Also check regex patterns for weighted calc
            for pattern, canonical_name in _tool_regexes:
                if re.search(pattern, txt_lower):
                    current_max = tool_max_weights.get(canonical_name, 0.0)
                    if w > current_max:
                        tool_max_weights[canonical_name] = w
        
        # Calculate Weighted Tool Count
        weighted_tool_count = sum(tool_max_weights.values())

        # Confidence Score Calculation (AC4)
        # Based on number of distinct sources provided
        distinct_sources = len(text_segments.keys())
        if distinct_sources >= 3:
            confidence = 1.0 # High
        elif distinct_sources == 2:
            confidence = 0.8 # Medium
        elif distinct_sources == 1:
             # If strictly only homepage, low
             if "homepage" in text_segments:
                 confidence = 0.5
             else:
                 confidence = 0.7 # Maybe a blog post only
        else:
             confidence = 0.0

        # Conflict Resolution / Marketing Only Detection
        # Logic: High AI Keywords on Homepage/Press BUT Zero on GitHub/Eng Blog
        # IR content with AI keywords prevents marketing-only flag (investor commitments are credible)
        marketing_only = False
        homepage_has_ai = "homepage" in sources_map["ai_keywords"]
        eng_sources = ["github", "engineering_blog", "job_posting", "job_posting_verified", "ats_link", "careers_fallback"]
        eng_has_ai = any(s in sources_map["ai_keywords"] for s in eng_sources) or any(s in sources_map["tool_stack"] for s in eng_sources)
        ir_has_ai = "investor_relations" in sources_map["ai_keywords"]

        total_keywords = non_eng_keywords + eng_ai_keywords
        if homepage_has_ai and not eng_has_ai and not ir_has_ai and total_keywords > 5:
             marketing_only = True

        # Count news-type sources analyzed
        news_sources_found = sum(1 for st in text_segments.keys() if st in NEWS_SOURCE_TYPES)

        # AI Platform Provider Detection
        # Companies that BUILD and PROVIDE AI tools/platforms to others are
        # benchmark transformational companies (e.g., Google, Anthropic, OpenAI).
        # Detection: AI-focused sources contain provider-language content — signs
        # the company ships AI products for external use, not just uses AI internally.
        ai_provider_indicators = [
            "our api", "our sdk", "our model", "our platform",
            "api reference", "api documentation",
            "developer documentation", "developer console",
            "ai studio", "ai platform", "model api",
            "inference api", "inference endpoint",
            "fine-tune", "fine tuning", "model deployment",
            "playground", "model serving", "deploy model",
            "foundation model", "large language model",
            "embed our", "build with our", "integrate with our",
        ]
        # Check AI-focused source types for provider language.
        # subdomain_ai is the strongest signal; engineering_blog and homepage
        # can also contain product descriptions for AI platform companies.
        ai_focused_types = {"subdomain_ai", "subdomain_dev", "subdomain_cloud", "engineering_blog"}
        is_ai_platform_provider = False

        for st in ai_focused_types:
            if st in text_segments:
                content = text_segments[st].lower()
                provider_hits = sum(1 for ind in ai_provider_indicators if ind in content)
                if provider_hits >= 3:
                    is_ai_platform_provider = True
                    break

        return SignalData(
            ai_keywords=non_eng_keywords,
            agentic_signals=min(agentic_count, 15),
            tool_stack=list(tools_found),
            non_eng_ai_roles=min(non_eng_score, 15),
            ai_in_it_signals=min(eng_ai_keywords, 15),
            has_ai_platform_team=has_platform_team,
            is_ai_platform_provider=is_ai_platform_provider,
            jobs_analyzed=len(text_segments),
            source_attribution=sources_map,
            marketing_only=marketing_only,
            weighted_tool_count=weighted_tool_count,
            confidence_score=confidence,
            ai_success_points=ai_success_points,
            ai_plan_points=ai_plan_points,
            ai_generic_points=ai_generic_points,
            news_sources_found=news_sources_found,
        )

    def _find_job_links(self, html: str, base_url: str) -> list[str]:
        """Parse HTML to find likely job posting links, including ATS embeds."""
        if not html:
            return []

        ats_detector = ATSDetector()
        soup = BeautifulSoup(html, "html.parser")
        links = set()

        # Story 4.3 AC1: Capture ATS links (external job boards)
        ats_links = ats_detector.extract_ats_links(html)
        links.update(ats_links)

        # Heuristic: Links containing "job", "career", "role", "detail" in href
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base_url, href)

            # Skip non-http
            if not full_url.startswith("http"):
                continue

            # Skip same page anchors
            if full_url.split("#")[0] == base_url.split("#")[0]:
                continue

            # Simple keyword matching in URL or text
            lower_href = href.lower()
            lower_text = a.get_text().lower()

            keywords = ["job", "career", "position", "role", "detail", "apply"]
            if any(k in lower_href for k in keywords) or "job" in lower_text:
                links.add(full_url)

        # Filter for job-specific structure
        filtered_links = []
        for link in links:
            # ATS links always pass through
            if ats_detector.is_ats_url(link):
                filtered_links.append(link)
            elif "/job/" in link or "/careers/" in link:
                filtered_links.append(link)
            elif len(link) > len(base_url) + 10:  # If distinct path
                filtered_links.append(link)

        return list(set(filtered_links))[:10]  # Up to 10 candidates

    async def _emergency_crawl(self, base_url: str, homepage_html: str, depth: int = 2) -> list[str]:
        """
        Story 4.3 AC2: Emergency Crawl when discovery search fails.

        Follows internal links from the homepage looking for /jobs, /careers,
        /apply paths, then extracts job links from those subpages.
        """
        if not homepage_html:
            return []

        parsed_base = urlparse(base_url)
        base_domain = parsed_base.netloc

        soup = BeautifulSoup(homepage_html, "html.parser")
        career_subpages = set()

        # Find internal links that look like career/job listing pages
        career_patterns = ["career", "job", "opening", "position", "team", "work-with-us", "join"]
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)

            # Only follow same-domain links
            if parsed.netloc and parsed.netloc != base_domain:
                # But allow known subdomains (careers.company.com)
                if not parsed.netloc.endswith(base_domain.replace("www.", "")):
                    continue

            lower_path = parsed.path.lower()
            if any(p in lower_path for p in career_patterns):
                career_subpages.add(full_url)

        if not career_subpages:
            return []

        # Depth 2: Scrape those subpages and extract job links from them
        all_job_links = []
        subpage_tasks = [self.scraper.scrape(sp) for sp in list(career_subpages)[:5]]
        subpage_results = await asyncio.gather(*subpage_tasks)

        for result in subpage_results:
            if result.success and result.raw_html:
                links = self._find_job_links(result.raw_html, result.url)
                all_job_links.extend(links)

        return list(set(all_job_links))[:10]

    async def manual_rescore(
        self,
        company_name: str,
        careers_url: str,
        evidence_urls: list[str] = None,
        research_mode: bool = False
    ) -> dict:
        """
        Story 4-6: Manually rescore a company with optional evidence URLs.

        Args:
            company_name: Name of the company
            careers_url: Main careers URL
            evidence_urls: Optional list of evidence URLs to scrape
            research_mode: If True, auto-discover sources via DiscoveryService

        Returns:
            dict with score result and metadata
        """
        from app.services.discovery import DiscoveryService
        from app.models.company import CompanySource
        from app.models.enums import SourceType

        evidence_urls = evidence_urls or []
        all_urls = list(set(evidence_urls))

        # Load existing saved sources for this company
        extracted = tldextract.extract(careers_url)
        root_domain = f"{extracted.domain}.{extracted.suffix}"

        stmt = select(Company).where(
            (Company.domain == root_domain) | (Company.name == company_name)
        )
        # Fix: handle duplicates gracefully (pick first)
        results = self.db.execute(stmt).scalars().all()
        company = results[0] if results else None

        if company:
            # Load existing sources
            source_stmt = select(CompanySource).where(
                CompanySource.company_id == company.id,
                CompanySource.is_active == True
            )
            existing_sources = self.db.execute(source_stmt).scalars().all()
            all_urls.extend([s.url for s in existing_sources])

        # Research mode: auto-discover sources
        if research_mode:
            discovery = DiscoveryService()
            # Fix: Use find_sources(name, domain) and extract URLs
            # extract domain from careers_url or company_name?
            # We already computed root_domain above.
            discovered_items = discovery.find_sources(company_name, root_domain)
            if discovered_items:
                all_urls.extend([item["url"] for item in discovered_items])

        # Deduplicate
        all_urls = list(set(all_urls))

        # Fallback to careers_url if no evidence
        if not all_urls and careers_url:
            all_urls = [careers_url]

        # Scrape all URLs and categorize by detected source type
        # M5 Fix: Use shared utility function
        from app.utils.source_detection import detect_source_type
        
        text_segments = {}
        scrape_results = []

        for url in all_urls:
            try:
                result = await self.scraper.scrape(url)
                if result.success:
                    text = result.extracted_text or ""
                    source_type = detect_source_type(url, text)
                    
                    # Append to existing segment or create new
                    if source_type in text_segments:
                        text_segments[source_type] += "\n" + text
                    else:
                        text_segments[source_type] = text
                    
                    scrape_results.append({"url": url, "status": "success", "source_type": source_type, "chars": len(text)})
                else:
                    scrape_results.append({"url": url, "status": "failed", "error": result.error_message})
            except Exception as e:
                scrape_results.append({"url": url, "status": "error", "error": str(e)})

        # Extract signals with categorized segments
        signals = self._extract_signals_heuristically(text_segments)
        signals.jobs_analyzed = len(all_urls)

        # Calculate score
        score_result = self.calculator.calculate(company_name, signals)

        # Get or create company
        if not company:
            company = self._get_or_create_company(company_name, root_domain, careers_url)

        # Save score
        new_score = Score(
            company_id=company.id,
            score=score_result.score,
            category=score_result.category,
            signals=score_result.signals.to_dict(),
            component_scores=score_result.component_scores,
            evidence=score_result.evidence + all_urls
        )
        self.db.add(new_score)

        # Save new sources for future use
        saved_sources = 0
        for url in all_urls:
            existing = self.db.execute(
                select(CompanySource).where(
                    CompanySource.company_id == company.id,
                    CompanySource.url == url
                )
            ).scalars().first()

            if not existing:
                source_type = SourceType.BLOG if "blog" in url.lower() else (
                    SourceType.GITHUB if "github" in url.lower() else SourceType.OTHER
                )
                new_source = CompanySource(
                    company_id=company.id,
                    url=url,
                    source_type=source_type.value,
                    is_active=True
                )
                self.db.add(new_source)
                saved_sources += 1

        self.db.commit()

        return {
            "company_name": company_name,
            "score": round(score_result.score, 1),
            "category": score_result.category.value,
            "component_scores": score_result.component_scores,
            "sources_scraped": len(all_urls),
            "sources_saved": saved_sources,
            "scrape_results": scrape_results
        }

