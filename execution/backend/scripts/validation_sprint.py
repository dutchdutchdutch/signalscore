"""
Validation Sprint: Signal Extraction vs Generic Prompts

This script runs the validation experiment:
- Path A: Generic LLM prompt for AI readiness rating
- Path B: Scraped job data + signal extraction

Test Companies (4 categories):
- High: Shopify, Stripe
- Medium-High: GitHub
- Medium-Low: Target
- Low: Local bank / traditional enterprise
"""

import asyncio
import json
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class TestCompany:
    """Company to test in the validation sprint."""
    name: str
    careers_url: str
    expected_category: str  # high, medium-high, medium-low, low
    notes: str


# Test companies spanning the 4 categories
TEST_COMPANIES = [
    TestCompany(
        name="Shopify",
        careers_url="https://www.shopify.com/careers",
        expected_category="high",
        notes="E-commerce giant with major AI initiatives - Sidekick AI, Shop AI, etc."
    ),
    TestCompany(
        name="Stripe",
        careers_url="https://stripe.com/jobs",
        expected_category="high", 
        notes="FinTech leader - Radar ML, payment optimization, fraud detection"
    ),
    TestCompany(
        name="Datadog",
        careers_url="https://careers.datadoghq.com",
        expected_category="medium-high",
        notes="Observability platform - ML for anomaly detection, growing AI features"
    ),
    TestCompany(
        name="Target",
        careers_url="https://corporate.target.com/careers",
        expected_category="medium-low",
        notes="Traditional retail with AI aspirations but primarily in supply chain"
    ),
    TestCompany(
        name="State Farm",
        careers_url="https://www.statefarm.com/careers",
        expected_category="low",
        notes="Traditional insurance - likely limited AI adoption beyond IT"
    ),
]


# Signal categories to extract from job postings
SIGNAL_CATEGORIES = {
    "ai_role_density": {
        "description": "Percentage of roles with AI/ML in title or core requirements",
        "keywords": ["AI", "ML", "Machine Learning", "Deep Learning", "LLM", "GPT", "NLP"],
        "weight": 3,  # High importance
    },
    "agentic_signals": {
        "description": "References to autonomous systems, agents, automation orchestration",
        "keywords": ["agent", "agentic", "autonomous", "automation", "orchestration", "workflow automation"],
        "weight": 3,
    },
    "tool_stack": {
        "description": "Modern AI/ML tools mentioned in job requirements",
        "keywords": ["PyTorch", "TensorFlow", "HuggingFace", "LangChain", "OpenAI", "Anthropic", "Claude", "Bedrock"],
        "weight": 2,
    },
    "ai_platform_team": {
        "description": "Dedicated AI/ML platform or infrastructure team signals",
        "keywords": ["AI Platform", "ML Platform", "MLOps", "Model serving", "Feature store"],
        "weight": 2,
    },
    "non_eng_ai_roles": {
        "description": "AI mentioned in non-engineering roles (Legal, Marketing, Ops, etc.)",
        "domains": ["Legal", "Marketing", "Operations", "HR", "Finance", "Product", "Sales"],
        "weight": 4,  # Highest importance - breadth signal
    },
    "copilot_adoption": {
        "description": "References to AI assistants, copilots in job requirements",
        "keywords": ["Copilot", "GitHub Copilot", "AI assistant", "ChatGPT", "coding assistant"],
        "weight": 1,  # Low signal - table stakes
    },
}


# Prompts for analysis
GENERIC_PROMPT = """
Rate {company_name}'s AI readiness on a scale of 1-10.

Provide:
1. Overall score (1-10)
2. One paragraph summary of their AI maturity
3. Key evidence for your rating

Focus on: How deeply has AI been integrated into their core business operations 
and workforce, not just their products?
"""

SIGNAL_EXTRACTION_PROMPT = """
Analyze the following job postings from {company_name} to assess their AI readiness.

Job Postings Data:
{job_data}

Extract and count:
1. AI/ML Role Density: What % of roles mention AI/ML in title or requirements?
2. Agentic Signals: Any mentions of agents, autonomous systems, workflow automation?
3. Tool Stack: Which modern AI tools are mentioned (PyTorch, LangChain, etc)?
4. AI Platform: Evidence of dedicated AI/ML platform or infrastructure team?
5. Non-Engineering AI: AI mentioned in Legal, Marketing, Ops, HR, Finance roles?
6. Copilot Adoption: References to AI coding assistants?

Then provide:
- Overall AI Readiness Score (1-10) with justification
- Category: High / Medium-High / Medium-Low / Low
- Key quotes or evidence from job postings
- Confidence level (High/Medium/Low) based on data quality
"""


async def run_generic_analysis(company: TestCompany) -> dict:
    """
    Path A: Run generic LLM prompt without scraped data.
    
    Uses LLM's training data knowledge about the company.
    """
    # TODO: Integrate with actual LLM API
    # For now, return placeholder
    return {
        "company": company.name,
        "path": "A - Generic Prompt",
        "prompt": GENERIC_PROMPT.format(company_name=company.name),
        "response": None,  # Will be filled by LLM
        "timestamp": datetime.now().isoformat(),
    }


async def scrape_and_analyze(company: TestCompany) -> dict:
    """
    Path B: Scrape job postings then analyze with LLM.
    
    Uses real-time scraped data for signal extraction.
    """
    # Import our scraper - add parent directory to path
    import sys
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.dirname(script_dir)
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    
    from app.services.scrapers import ScraperOrchestrator, ScraperConfig
    
    # Step 1: Scrape careers page
    scraper = ScraperOrchestrator(ScraperConfig())
    careers_result = await scraper.scrape(company.careers_url)
    
    # Get content from result (field is extracted_text)
    content = careers_result.extracted_text or ""
    
    # Step 2: Extract job links (if careers page has listings)
    # For now, use the careers page content directly
    
    result = {
        "company": company.name,
        "path": "B - Scraped Analysis",
        "scraped_content": {
            "careers_page": {
                "url": company.careers_url,
                "content_length": len(content),
                "success": careers_result.success,
                "strategy": careers_result.strategy_used.value if careers_result.strategy_used else "unknown",
            }
        },
        "raw_content": content[:10000],  # Store first 10k chars for analysis
        "prompt": SIGNAL_EXTRACTION_PROMPT.format(
            company_name=company.name,
            job_data=content[:5000] if careers_result.success else "FAILED TO SCRAPE"
        ),
        "response": None,  # Will be filled by LLM
        "timestamp": datetime.now().isoformat(),
    }
    
    return result


async def run_validation_sprint():
    """
    Run the full validation sprint for all test companies.
    """
    print("=" * 60)
    print("VALIDATION SPRINT: Signal Extraction vs Generic Prompts")
    print("=" * 60)
    print()
    
    results = []
    
    for company in TEST_COMPANIES:
        print(f"\n{'─' * 40}")
        print(f"Testing: {company.name} (Expected: {company.expected_category})")
        print(f"{'─' * 40}")
        
        # Path A: Generic prompt
        print("  [A] Running generic prompt analysis...")
        path_a = await run_generic_analysis(company)
        
        # Path B: Scraped data analysis  
        print("  [B] Scraping and analyzing job data...")
        path_b = await scrape_and_analyze(company)
        
        results.append({
            "company": company.name,
            "expected_category": company.expected_category,
            "notes": company.notes,
            "path_a": path_a,
            "path_b": path_b,
        })
        
        # Print scrape status
        if path_b["scraped_content"]["careers_page"]["success"]:
            chars = path_b["scraped_content"]["careers_page"]["content_length"]
            strategy = path_b["scraped_content"]["careers_page"]["strategy"]
            print(f"  ✓ Scraped {chars} chars using {strategy}")
        else:
            print(f"  ✗ Failed to scrape careers page")
    
    # Save results
    output_file = "validation_sprint_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'=' * 60}")
    print(f"Results saved to: {output_file}")
    print(f"{'=' * 60}")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_validation_sprint())
