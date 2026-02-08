
import asyncio
import sys
import os
import argparse
from typing import List, Optional

# Add parent directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.scoring_service import ScoringService
from app.services.scrapers import ScraperOrchestrator, ScraperConfig
from app.services.discovery_service import DiscoveryService
from app.core.database import SessionLocal
from app.models.company import Company, Score, CompanySource
from app.models.enums import SourceType
from sqlalchemy import select

async def scrape_urls(urls: List[str]) -> dict:
    """Helper to scrape multiple URLs and return text segments categorized by source type."""
    # M5 Fix: Use shared utility function
    from app.utils.source_detection import detect_source_type
    
    scraper = ScraperOrchestrator(ScraperConfig())
    text_segments = {}
    
    print(f"Scraping {len(urls)} sources...")
    results = await asyncio.gather(*[scraper.scrape(url) for url in urls])
    
    for i, res in enumerate(results):
        if res.success:
            text = res.extracted_text or ""
            source_type = detect_source_type(urls[i], text)
            print(f"  ✅ Scraped {urls[i]}: {len(text)} chars [{source_type}]")
            
            # Append to existing segment or create new
            if source_type in text_segments:
                text_segments[source_type] += "\n" + text
            else:
                text_segments[source_type] = text
        else:
            print(f"  ❌ Failed {urls[i]}: {res.error_message}")
            
    return text_segments


def load_existing_sources(db, company: Company) -> List[str]:
    """Load active sources for a company."""
    if not company:
        return []
    stmt = select(CompanySource).where(
        CompanySource.company_id == company.id,
        CompanySource.is_active == True
    )
    sources = db.execute(stmt).scalars().all()
    return [s.url for s in sources]


def save_source(db, company: Company, url: str, source_type: SourceType = SourceType.OTHER):
    """Save a new source URL for a company if not already exists."""
    existing = db.execute(
        select(CompanySource).where(
            CompanySource.company_id == company.id,
            CompanySource.url == url
        )
    ).scalars().first()
    
    if not existing:
        new_source = CompanySource(
            company_id=company.id,
            url=url,
            source_type=source_type.value,
            is_active=True
        )
        db.add(new_source)
        return True
    return False

async def debug_mode(company_name: str, url: str):
    """Debug mode: Scrape and print signals without saving."""
    print(f"🔧 DEBUG MODE: Analyzing {company_name} ({url})")
    
    # Scrape
    text = await scrape_urls([url])
    
    # Initialize Service (No DB needed for heuristic extraction, but class requires it)
    # used MockDB approach from debug_nordstrom.py implies we can pass None if careful
    service = ScoringService(None) 
    
    print("\n--- Extracted Signals (Heuristic) ---")
    signals = service._extract_signals_heuristically(text)
    
    print(f"AI Keywords: {signals.ai_keywords}")
    print(f"Agentic Signals: {signals.agentic_signals}")
    print(f"Tool Stack: {signals.tool_stack}")
    print(f"Platform Team: {signals.has_ai_platform_team}")
    
    # Calculate potential score
    score_result = service.calculator.calculate(company_name, signals)
    print(f"\n--- Potential Score ---")
    print(f"Score: {score_result.score}")
    print(f"Category: {score_result.category}")
    print("\n(Not saved to database)")


async def evidence_mode(company_name: str, main_url: str, evidence_urls: List[str], research: bool = False):
    """Evidence mode: Scrape specific URLs and save score."""
    
    # Connect to DB early to load existing sources
    db = SessionLocal()
    try:
        stmt = select(Company).where(Company.name == company_name)
        company = db.execute(stmt).scalar_one_or_none()
        
        # Load existing saved sources
        existing_sources = load_existing_sources(db, company)
        if existing_sources:
            print(f"📂 Loaded {len(existing_sources)} saved sources from database.")
        
        all_urls = list(set(evidence_urls + existing_sources)) if existing_sources else list(evidence_urls)
        
        if research:
            print(f"🕵️‍♀️ RESEARCH MODE: Automatically discovering signals for {company_name}")
            discovery = DiscoveryService()
            discovered = discovery.discover_sources(company_name)
            if discovered:
                print(f"  + Added {len(discovered)} discovered sources")
                all_urls.extend(discovered)
        
        # Deduplicate
        all_urls = list(set(all_urls))
        
        # Ensure main URL is included if no other evidence
        if not all_urls and main_url:
            all_urls = [main_url]
            
        print(f"🚀 EVIDENCE MODE: Rescoring {company_name} with {len(all_urls)} evidence sources")
        
        # Scrape all evidence (returns categorized text_segments dict)
        text_segments = await scrape_urls(all_urls)
        
        service = ScoringService(db)
        
        # Extract signals from categorized segments
        signals = service._extract_signals_heuristically(text_segments)
        signals.jobs_analyzed = len(all_urls)
        
        # Calculate
        score_result = service.calculator.calculate(company_name, signals)
        
        print("\n📊 New Score Result:")
        print(f"  Score: {score_result.score}")
        print(f"  Category: {score_result.category}")
        
        print("\n🧩 Component Scores:")
        for k, v in score_result.component_scores.items():
            print(f"  - {k}: {v}")
        
        # Update DB
        print("\nUpdating Database...")
        stmt = select(Company).where(Company.name == company_name)
        company = db.execute(stmt).scalar_one_or_none()
        
        if not company:
            print(f"  ⚠️ {company_name} record not found! Creating new one...")
            # Extract domain from main_url
            domain = main_url.replace("https://", "").replace("http://", "").split("/")[0]
            if "www." in domain: domain = domain.replace("www.", "")
            
            company = service._get_or_create_company(company_name, domain, main_url)
        
        # Save
        new_score = Score(
            company_id=company.id,
            score=score_result.score,
            category=score_result.category,
            signals=score_result.signals.to_dict(),
            component_scores=score_result.component_scores,
            evidence=score_result.evidence + all_urls
        )
        db.add(new_score)
        db.commit()
        print("  ✅ Database updated successfully!")
        
        # Save successful sources for future use
        saved_count = 0
        for url in all_urls:
            source_type = SourceType.BLOG if "blog" in url.lower() else (
                SourceType.GITHUB if "github" in url.lower() else SourceType.OTHER
            )
            if save_source(db, company, url, source_type):
                saved_count += 1
        if saved_count > 0:
            db.commit()
            print(f"  💾 Saved {saved_count} new source URLs for future rescoring.")
        
    finally:
        db.close()

async def standard_mode(company_name: str, url: str):
    """Standard mode: Trigger standard scoring logic."""
    print(f"🔄 STANDARD MODE: Scoring {company_name} via standard service pipeline")
    
    db = SessionLocal()
    try:
        service = ScoringService(db)
        # We call score_company which handles scraping, deep crawling, and saving
        await service.score_company(url)
        
        # Verify
        stmt = select(Company).where(Company.careers_url == url)
        company = db.execute(stmt).scalar_one_or_none()
        if company and company.scores:
            latest = company.scores[-1]
            print(f"\n✅ Scored successfully. Latest: {latest.score} ({latest.category})")
        else:
            print("\n⚠️ Scoring finished but no score found (check logs for errors).")
            
    finally:
        db.close()


async def main():
    parser = argparse.ArgumentParser(description="SignalScore Rescoring Tool")
    parser.add_argument("--company", required=True, help="Company Name")
    parser.add_argument("--url", required=True, help="Main Careers URL")
    parser.add_argument("--evidence", nargs="*", help="List of specific evidence URLs")
    parser.add_argument("--research", action="store_true", help="Automatically research company blogs/github")
    parser.add_argument("--debug", action="store_true", help="Run in debug mode (no save)")
    
    args = parser.parse_args()
    
    if args.debug:
        await debug_mode(args.company, args.url)
    elif args.evidence is not None or args.research: 
        # Trigger evidence mode if evidence provided OR research requested
        evidence = args.evidence if args.evidence else []
        await evidence_mode(args.company, args.url, evidence, args.research)
    else:
        # Check if company has saved sources -> redirect to evidence mode automatically
        db = SessionLocal()
        try:
            stmt = select(Company).where(Company.name == args.company)
            company = db.execute(stmt).scalar_one_or_none()
            sources = load_existing_sources(db, company) if company else []
        finally:
            db.close()
        
        if sources:
            print(f"📂 Found {len(sources)} saved sources for {args.company}. Using enhanced analysis.")
            await evidence_mode(args.company, args.url, [], False)
        else:
            await standard_mode(args.company, args.url)

if __name__ == "__main__":
    asyncio.run(main())
