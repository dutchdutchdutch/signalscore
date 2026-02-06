
from typing import List, Set
from ddgs import DDGS
import logging

class DiscoveryService:
    """
    Service to find additional signal sources (blogs, github) for a company.
    Uses DuckDuckGo Search via 'ddgs' library.
    """
    
    def __init__(self):
        # Configure logging just for this run/service context if needed
        self.logger = logging.getLogger(__name__)

    def discover_sources(self, company_name: str, max_results: int = 3) -> List[str]:
        """
        Search for engineering blogs, open source profiles, and tech stacks.
        Returns a list of unique URLs.
        """
        print(f"🔎 Analyzing web footprint for: {company_name}")
        
        queries = [
            f"{company_name} engineering blog",
            f"{company_name} tech blog",
            f"{company_name} artificial intelligence blog",
            f"{company_name} open source github",
            f"how {company_name} uses machine learning"
        ]
        
        found_urls: Set[str] = set()
        
        # Use context manager for DDGS
        with DDGS() as ddgs:
            for q in queries:
                try:
                    # ddgs.text() returns an iterable of dicts {'title':..., 'href':..., 'body':...}
                    results = list(ddgs.text(q, max_results=2))
                    
                    for res in results:
                        url = res.get('href')
                        if self._is_valid_source(url, company_name):
                            found_urls.add(url)
                            print(f"  ✅ Discovered: {res.get('title')} -> {url}")
                            
                except Exception as e:
                    print(f"  ⚠️ Search error for query '{q}': {e}")
                    
        return list(found_urls)

    def _is_valid_source(self, url: str, company_name: str) -> bool:
        """Filter out obviously irrelevant sources or spam."""
        if not url: return False
        
        # Lowercase for checking
        url_lower = url.lower()
        company_clean = company_name.lower().replace(" ", "")
        
        # Blocklist
        blocklist = [
            "glassdoor.com", "linkedin.com/jobs", "indeed.com", 
            "levels.fyi", "teamblind.com", "comparably.com"
        ]
        if any(b in url_lower for b in blocklist):
            return False
            
        return True
