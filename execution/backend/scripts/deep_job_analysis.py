"""
Deep Job Scraping: Extract and analyze individual job postings.

This script:
1. Extracts job links from careers pages (using browser for JS-heavy sites)
2. Scrapes individual job descriptions
3. Counts AI-related signals for comparison
"""

import asyncio
import json
import re
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(script_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.scrapers import ScraperOrchestrator, ScraperConfig


@dataclass
class JobPosting:
    """A single job posting with extracted signals."""
    url: str
    title: str
    department: str = ""
    location: str = ""
    raw_content: str = ""
    
    # Signal counts
    ai_keywords: list[str] = field(default_factory=list)
    tool_stack: list[str] = field(default_factory=list)
    agentic_signals: list[str] = field(default_factory=list)
    is_non_eng_role: bool = False
    has_ai_in_requirements: bool = False


@dataclass 
class CompanyAnalysis:
    """Analysis results for a company's job postings."""
    company: str
    jobs_analyzed: int
    total_ai_keywords: int
    ai_role_percentage: float
    non_eng_ai_roles: int
    tools_mentioned: list[str]
    agentic_signals_count: int
    sample_quotes: list[str]
    
    def to_dict(self):
        return {
            "company": self.company,
            "jobs_analyzed": self.jobs_analyzed,
            "total_ai_keywords": self.total_ai_keywords,
            "ai_role_percentage": self.ai_role_percentage,
            "non_eng_ai_roles": self.non_eng_ai_roles,
            "tools_mentioned": self.tools_mentioned,
            "agentic_signals_count": self.agentic_signals_count,
            "sample_quotes": self.sample_quotes,
        }


# AI Signal Patterns
AI_KEYWORDS = [
    r'\bAI\b', r'\bartificial intelligence\b',
    r'\bML\b', r'\bmachine learning\b',
    r'\bdeep learning\b', r'\bneural network\b',
    r'\bLLM\b', r'\blarge language model\b',
    r'\bNLP\b', r'\bnatural language\b',
    r'\bcomputer vision\b', r'\bCV\b',
    r'\bGPT\b', r'\bClaude\b', r'\bBedrock\b',
    r'\bprompt engineering\b',
]

TOOL_STACK = [
    r'\bPyTorch\b', r'\bTensorFlow\b', r'\bJAX\b',
    r'\bHuggingFace\b', r'\bTransformers\b',
    r'\bLangChain\b', r'\bLlamaIndex\b',
    r'\bOpenAI\b', r'\bAnthropic\b',
    r'\bMLflow\b', r'\bKubeflow\b', r'\bSageMaker\b',
    r'\bVertex AI\b', r'\bDatabricks\b',
    r'\bCopilot\b', r'\bGitHub Copilot\b',
]

AGENTIC_SIGNALS = [
    r'\bagent\b', r'\bagentic\b', r'\bautonomous\b',
    r'\bworkflow automation\b', r'\bRPA\b',
    r'\borchestrat\w+\b', r'\bautomation\b',
    r'\bself-service\b', r'\bno-code\b', r'\blow-code\b',
]

NON_ENG_DEPARTMENTS = [
    'legal', 'marketing', 'sales', 'finance', 
    'hr', 'human resources', 'operations', 'product',
    'customer', 'support', 'success', 'admin',
]


def extract_signals(content: str) -> tuple[list[str], list[str], list[str]]:
    """Extract AI signals from job content."""
    content_lower = content.lower()
    
    ai_matches = []
    for pattern in AI_KEYWORDS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        ai_matches.extend(matches)
    
    tool_matches = []
    for pattern in TOOL_STACK:
        matches = re.findall(pattern, content, re.IGNORECASE)
        tool_matches.extend(matches)
    
    agentic_matches = []
    for pattern in AGENTIC_SIGNALS:
        matches = re.findall(pattern, content, re.IGNORECASE)
        agentic_matches.extend(matches)
    
    return ai_matches, tool_matches, agentic_matches


def is_non_engineering_role(title: str, department: str) -> bool:
    """Check if a role is in a non-engineering department."""
    combined = f"{title} {department}".lower()
    
    # Exclude if clearly engineering
    eng_signals = ['engineer', 'developer', 'software', 'data scientist', 'ml ']
    if any(sig in combined for sig in eng_signals):
        return False
    
    # Check for non-eng departments
    return any(dept in combined for dept in NON_ENG_DEPARTMENTS)


def extract_quotes(content: str, max_quotes: int = 3) -> list[str]:
    """Extract relevant AI-related quotes from content."""
    quotes = []
    sentences = re.split(r'[.!?]', content)
    
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 20 or len(sentence) > 300:
            continue
        
        # Check if sentence contains AI keywords
        for pattern in AI_KEYWORDS[:5]:  # Check first few patterns
            if re.search(pattern, sentence, re.IGNORECASE):
                quotes.append(sentence)
                break
        
        if len(quotes) >= max_quotes:
            break
    
    return quotes


# Known job URLs from browser exploration
SHOPIFY_JOBS = [
    {
        "url": "https://www.shopify.com/careers/applied-ml-engineering-genai-ai-agent_b89676a7-b361-450c-a7de-0bf9a57121bd",
        "title": "Applied ML Engineering - GenAI, AI Agent",
        "department": "Engineering"
    },
    {
        "url": "https://www.shopify.com/careers/applied-machine-learning-engineers_19b9dea6-f028-4362-aae5-ab6ef70560a7",
        "title": "Applied Machine Learning Engineers",
        "department": "Engineering"
    },
    {
        "url": "https://www.shopify.com/careers/applied-machine-learning-engineering-managers_54914cfb-394f-486f-bd27-69627f8505d0",
        "title": "Applied Machine Learning Engineering Managers",
        "department": "Engineering"
    },
    {
        "url": "https://www.shopify.com/careers/data-engineers_86a43b4a-3193-4cee-972a-faea0b787eb2",
        "title": "Data Engineers",
        "department": "Engineering"
    },
    {
        "url": "https://www.shopify.com/careers/c-search-ranking-engineer_13e77b6a-e6d9-458a-a376-6447cb145671",
        "title": "C++ Search Ranking Engineer",
        "department": "Engineering"
    },
]

# Target jobs - discovered via browser exploration
TARGET_JOBS = [
    {
        "url": "https://corporate.target.com/jobs/w09/37/merch-lead-engineer-backend",
        "title": "Lead Engineer Backend (Generative AI)",
        "department": "Target Tech"
    },
    {
        "url": "https://corporate.target.com/jobs/w06/75/sr-java-engineer",
        "title": "Sr. Java Engineer",
        "department": "Target Tech"
    },
    {
        "url": "https://corporate.target.com/jobs/w10/99/lead-engineer,-penetration-tester",
        "title": "Lead Engineer, Penetration Tester",
        "department": "Target Tech"
    },
    {
        "url": "https://corporate.target.com/jobs/w81/15/sr-engineer-mobility",
        "title": "Sr. Engineer - Mobility",
        "department": "Target Tech"
    },
    {
        "url": "https://corporate.target.com/jobs/w80/89/director-guest-marketing-strategy,-beauty",
        "title": "Director Guest Marketing Strategy, Beauty",
        "department": "Marketing"
    },
]

# Nordstrom jobs - discovered via browser exploration
NORDSTROM_JOBS = [
    {
        "url": "https://careers.nordstrom.com/principal-data-science-ml-engineer-hybrid-seattle/job/3AC6EE50A67CC79A4B726B4EC47B7B75",
        "title": "Principal Data Science & ML Engineer",
        "department": "Engineering"
    },
    {
        "url": "https://careers.nordstrom.com/principal-engineer-digital-commerce-customer-platform-hybrid-seattle-wa/job/C94FA1E82919A9595E17F12BEDF3FFCC",
        "title": "Principal Engineer - Digital Commerce",
        "department": "Engineering"
    },
    {
        "url": "https://careers.nordstrom.com/data-engineer-2-hybrid-seattle-wa/job/633239DCFBE4D22821F36BE6CC17A20B",
        "title": "Data Engineer 2",
        "department": "Engineering"
    },
    {
        "url": "https://careers.nordstrom.com/sr-digital-marketing-specialist-product-feed-management-hybrid-seattle-wa/job/A25834A8A7CEC530333CF99047E46813",
        "title": "Sr. Digital Marketing Specialist, Product Feed Management",
        "department": "Marketing"
    },
    {
        "url": "https://careers.nordstrom.com/creative-designer-principal-hybrid-seattle-wa/job/9B5E96411FBA2C573F58152BFB987B04",
        "title": "Creative Designer Principal",
        "department": "Creative"
    },
]

# Tesla jobs - discovered via browser exploration
TESLA_JOBS = [
    # Engineering
    {
        "url": "https://www.tesla.com/careers/search/job/sr-mechanical-design-engineer-new-programs--227273",
        "title": "Senior Mechanical Design Engineer, New Programs",
        "department": "Engineering"
    },
    {
        "url": "https://www.tesla.com/careers/search/job/mechanical-design-engineer-battery-pack-battery-engineering-228631",
        "title": "Mechanical Design Engineer, Battery Pack",
        "department": "Engineering"
    },
    # Legal
    {
        "url": "https://www.tesla.com/careers/search/job/paralegal-259505",
        "title": "Paralegal",
        "department": "Legal"
    },
    {
        "url": "https://www.tesla.com/careers/search/job/243226",
        "title": "Sr. Paralegal, Litigation",
        "department": "Legal"
    },
    # Marketing
    {
        "url": "https://www.tesla.com/careers/search/job/lead-generation-specialist-240809",
        "title": "Lead Generation Specialist",
        "department": "Marketing"
    },
    {
        "url": "https://www.tesla.com/careers/search/job/consumer-engagement-specialist-content-focus-242933",
        "title": "Consumer Engagement Specialist - Content Focus",
        "department": "Marketing"
    },
]

# Stellantis jobs - discovered via browser exploration
STELLANTIS_JOBS = [
    # Engineering
    {
        "url": "https://careers.stellantis.com/job/22708116/launch-industrial-engineering-supervisor/",
        "title": "Launch Industrial Engineering Supervisor",
        "department": "Engineering"
    },
    {
        "url": "https://careers.stellantis.com/job/22362866/design-release-engineer-electric-drive-modules/",
        "title": "Design Release Engineer - Electric Drive Modules",
        "department": "Engineering"
    },
    # Marketing
    {
        "url": "https://careers.stellantis.com/job/22718377/brand-marketing-manager-midwest-business-center/",
        "title": "Brand Marketing Manager – Midwest Business Center",
        "department": "Marketing"
    },
    {
        "url": "https://careers.stellantis.com/job/22917220/crm-lifecycle-marketing-manager/",
        "title": "CRM Lifecycle Marketing Manager",
        "department": "Marketing"
    },
    # Legal/Compliance
    {
        "url": "https://careers.stellantis.com/job/22831476/eeo-compliance-specialist/",
        "title": "EEO Compliance Specialist",
        "department": "Legal/Compliance"
    },
    {
        "url": "https://careers.stellantis.com/job/22518167/risk-financing-manager-insurance-officer-na-/",
        "title": "Risk Financing Manager – Insurance Officer",
        "department": "Legal/Finance"
    },
]

TARGET_CAREERS_URL = "https://corporate.target.com/careers"

# Macy's jobs - discovered via browser exploration (Oracle HCM Cloud)
MACYS_JOBS = [
    {
        "url": "https://ebwh.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/84335/",
        "title": "Sr. Director, Enterprise AI Strategy and Enablement",
        "department": "Technology"
    },
    {
        "url": "https://ebwh.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/83629/",
        "title": "Sr. Director, Data Science - Customer + Digital",
        "department": "Technology"
    },
    {
        "url": "https://ebwh.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/84660/",
        "title": "Director, Data Engineering",
        "department": "Technology"
    },
    {
        "url": "https://ebwh.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/84342/",
        "title": "Principal, Engineer - Data Engineering",
        "department": "Technology"
    },
    {
        "url": "https://ebwh.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001/job/82222/",
        "title": "Senior Manager, Marketing Transformation",
        "department": "Marketing"
    },
]


async def scrape_job_posting(scraper: ScraperOrchestrator, job: dict) -> Optional[JobPosting]:
    """Scrape and analyze a single job posting."""
    print(f"    Scraping: {job['title'][:50]}...")
    
    result = await scraper.scrape(job["url"])
    
    if not result.success:
        print(f"    ✗ Failed to scrape: {result.error_message}")
        return None
    
    content = result.extracted_text or ""
    
    # Extract signals
    ai_keywords, tools, agentic = extract_signals(content)
    
    posting = JobPosting(
        url=job["url"],
        title=job["title"],
        department=job.get("department", ""),
        raw_content=content[:5000],  # Store first 5k chars
        ai_keywords=ai_keywords,
        tool_stack=tools,
        agentic_signals=agentic,
        is_non_eng_role=is_non_engineering_role(job["title"], job.get("department", "")),
        has_ai_in_requirements=len(ai_keywords) > 0,
    )
    
    print(f"    ✓ Found: {len(ai_keywords)} AI keywords, {len(tools)} tools, {len(agentic)} agentic signals")
    
    return posting


async def analyze_company(company_name: str, jobs: list[dict]) -> CompanyAnalysis:
    """Analyze all job postings for a company."""
    print(f"\n{'=' * 50}")
    print(f"Analyzing: {company_name}")
    print(f"{'=' * 50}")
    
    scraper = ScraperOrchestrator(ScraperConfig())
    
    postings = []
    for job in jobs:
        posting = await scrape_job_posting(scraper, job)
        if posting:
            postings.append(posting)
    
    if not postings:
        return CompanyAnalysis(
            company=company_name,
            jobs_analyzed=0,
            total_ai_keywords=0,
            ai_role_percentage=0,
            non_eng_ai_roles=0,
            tools_mentioned=[],
            agentic_signals_count=0,
            sample_quotes=[],
        )
    
    # Aggregate results
    all_ai_keywords = []
    all_tools = []
    all_agentic = []
    ai_roles = 0
    non_eng_ai = 0
    all_quotes = []
    
    for posting in postings:
        all_ai_keywords.extend(posting.ai_keywords)
        all_tools.extend(posting.tool_stack)
        all_agentic.extend(posting.agentic_signals)
        
        if posting.has_ai_in_requirements:
            ai_roles += 1
        
        if posting.is_non_eng_role and posting.has_ai_in_requirements:
            non_eng_ai += 1
        
        quotes = extract_quotes(posting.raw_content)
        all_quotes.extend(quotes)
    
    # Deduplicate tools
    unique_tools = list(set(t.lower() for t in all_tools))
    
    return CompanyAnalysis(
        company=company_name,
        jobs_analyzed=len(postings),
        total_ai_keywords=len(all_ai_keywords),
        ai_role_percentage=round(ai_roles / len(postings) * 100, 1),
        non_eng_ai_roles=non_eng_ai,
        tools_mentioned=unique_tools,
        agentic_signals_count=len(all_agentic),
        sample_quotes=all_quotes[:5],  # Top 5 quotes
    )


async def run_deep_analysis():
    """Run deep analysis on all companies for comparison."""
    print("=" * 70)
    print("DEEP JOB ANALYSIS: Signal Extraction from Individual Postings")
    print("=" * 70)
    
    # Define comparison groups
    comparisons = [
        {
            "name": "RETAIL: Target vs Nordstrom vs Macy's",
            "companies": [
                ("Target", TARGET_JOBS, "Medium-Low?"),
                ("Nordstrom", NORDSTROM_JOBS, "Medium?"),
                ("Macy's", MACYS_JOBS, "Low?"),
            ]
        },
        {
            "name": "AUTO: Tesla vs Stellantis",
            "companies": [
                ("Tesla", TESLA_JOBS, "High"),
                ("Stellantis", STELLANTIS_JOBS, "Medium-Low"),
            ]
        },
    ]
    
    all_analyses = []
    
    for comparison in comparisons:
        print(f"\n{'='*70}")
        print(f"  {comparison['name']}")
        print(f"{'='*70}")
        
        for company_name, jobs, expected in comparison["companies"]:
            analysis = await analyze_company(company_name, jobs)
            analysis.expected_category = expected  # Add expected category
            all_analyses.append(analysis)
    
    # Print results by comparison
    print("\n" + "=" * 70)
    print("COMPARISON RESULTS")
    print("=" * 70)
    
    for comparison in comparisons:
        print(f"\n### {comparison['name']}")
        print("-" * 50)
        
        comp_analyses = [a for a in all_analyses if a.company in [c[0] for c in comparison["companies"]]]
        
        for analysis in comp_analyses:
            print(f"\n📊 {analysis.company}")
            print(f"   Jobs Analyzed: {analysis.jobs_analyzed}")
            print(f"   AI Keywords: {analysis.total_ai_keywords}")
            print(f"   AI Role %: {analysis.ai_role_percentage}%")
            print(f"   Agentic Signals: {analysis.agentic_signals_count}")
            print(f"   Tools: {', '.join(analysis.tools_mentioned) or 'None'}")
    
    # Print comparison table
    print("\n" + "=" * 70)
    print("SIGNAL COMPARISON TABLE")
    print("=" * 70)
    
    print(f"\n{'Company':<15} {'AI Keywords':>12} {'AI Role %':>12} {'Agentic':>10} {'Tools':>8}")
    print("-" * 65)
    for a in all_analyses:
        print(f"{a.company:<15} {a.total_ai_keywords:>12} {a.ai_role_percentage:>11}% {a.agentic_signals_count:>10} {len(a.tools_mentioned):>8}")
    
    # Save results
    results = {
        "timestamp": datetime.now().isoformat(),
        "comparisons": [
            {
                "name": comp["name"],
                "companies": [c[0] for c in comp["companies"]]
            }
            for comp in comparisons
        ],
        "analysis": [a.to_dict() for a in all_analyses],
    }
    
    output_file = os.path.join(backend_dir, "deep_analysis_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n\nResults saved to: {output_file}")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_deep_analysis())
