#!/usr/bin/env python3
"""Quick scraper test script - run directly to verify scraper functionality."""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.scrapers import ScraperOrchestrator, ScraperStrategy


async def test_scraper():
    """Test the scraper with Shopify career pages."""
    
    print("=" * 60)
    print("SignalScore Scraper Test")
    print("=" * 60)
    
    orchestrator = ScraperOrchestrator()
    
    # Test URLs
    test_cases = [
        {
            "name": "Shopify Job Posting",
            "url": "https://www.shopify.com/careers/technical-program-manager_6f1f51d3-1659-4259-a99c-bf5c30662357",
            "expected_keywords": ["shopify", "technical", "program", "manager"],
        },
        {
            "name": "Shopify Engineering Careers",
            "url": "https://www.shopify.com/careers/disciplines/engineering-data",
            "expected_keywords": ["engineering", "data", "careers"],
        },
    ]
    
    results = []
    
    for test in test_cases:
        print(f"\n📡 Testing: {test['name']}")
        print(f"   URL: {test['url']}")
        
        result = await orchestrator.scrape(test['url'])
        
        if result.success:
            print(f"   ✅ SUCCESS - Strategy: {result.strategy_used.value}")
            print(f"   📄 Title: {result.title or 'N/A'}")
            print(f"   📝 Extracted text: {len(result.extracted_text or '')} chars")
            
            # Check for expected keywords
            text_lower = (result.extracted_text or "").lower()
            found_keywords = [kw for kw in test["expected_keywords"] if kw in text_lower]
            missing_keywords = [kw for kw in test["expected_keywords"] if kw not in text_lower]
            
            if found_keywords:
                print(f"   🔍 Found keywords: {', '.join(found_keywords)}")
            if missing_keywords:
                print(f"   ⚠️  Missing keywords: {', '.join(missing_keywords)}")
            
            # Show text snippet
            snippet = (result.extracted_text or "")[:300]
            print(f"\n   --- Text Preview ---\n   {snippet}...")
            
            results.append({"name": test["name"], "success": True})
        else:
            print(f"   ❌ FAILED: {result.error_message}")
            results.append({"name": test["name"], "success": False, "error": result.error_message})
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results if r["success"])
    failed = len(results) - passed
    
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['name']}")
    
    print(f"\nTotal: {passed}/{len(results)} passed")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(test_scraper())
    sys.exit(0 if success else 1)
