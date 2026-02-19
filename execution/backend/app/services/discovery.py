import logging
import time
import requests
from typing import List, Dict, Optional
from urllib.parse import urlparse

try:
    from googlesearch import search
except ImportError:
    # Fallback/Mock for environments where the library isn't installed yet
    def search(*args, **kwargs):
        raise ImportError("googlesearch-python not installed")

from app.models.company import CompanySource
from app.services.scrapers.ats_detector import ATSDetector

logger = logging.getLogger(__name__)

class DiscoveryService:
    """
    Service to discover satellite URLs (Engineering Blogs, GitHub, etc.)
    using search queries.
    """

    def __init__(self):
        self.ats_detector = ATSDetector()
        self.search_failed = False

    def find_sources(self, company_name: str, main_domain: str) -> List[Dict[str, str]]:
        """
        Main entry point. Performs multiple searches to find relevant sources.
        Returns a list of dicts: {'url': '...', 'type': '...'}
        """
        discovered = []
        
        # 1. Search for Engineering Blog
        blog_url = self._search_engineering_blog(company_name, main_domain)
        if blog_url:
            discovered.append({"url": blog_url, "type": "engineering_blog"})
            
        # 2. Search for GitHub Organization
        github_url = self._search_github_org(company_name)
        if github_url:
            discovered.append({"url": github_url, "type": "github"})

        # 3. Search for Careers Page (if external/subdomain)
        careers_url = self._search_careers(company_name, main_domain)
        if careers_url:
            discovered.append({"url": careers_url, "type": "careers"})
            
        # 4. Search for AI Product/Legal/Marketing (Targeting Middle Management)
        # We try to find specific job descriptions or team pages that mention agentic workflows
        # Query: company role (agent OR orchestration OR AI)
        for role in ["product manager", "marketing manager", "legal counsel"]:
            # We search for the role + keywords to find the JD that mentions them
            role_url = self._search_role(company_name, role, '("agent" OR "orchestration" OR "AI")')
            if role_url:
                 discovered.append({"url": role_url, "type": f"{role.split(' ')[0]}_role"})
 
        # 5. Search for "AI Conference/Speaking" (Targeting Executive Thought Leadership)
        # Query: company "AI" "Conference" "Speaker"
        # We try to find video platforms or slide decks or conference agendas
        conf_query = f'{company_name} "AI" "Conference" "Speaker"'
        conf_url = self._perform_search(conf_query, domain_filter=None, keyword_filter=None) # No strict keyword filter, maybe "conference"
        if conf_url:
             discovered.append({"url": conf_url, "type": "conference_speaking"})

        # 6. Probe for corporate pages (IR, newsroom, press) — no Google query needed
        corporate_pages = self._probe_corporate_pages(main_domain)
        discovered.extend(corporate_pages)

        # 7. Search for recent news articles mentioning AI (1 Google query)
        news_results = self._search_news_articles(company_name)
        discovered.extend(news_results)

        # 8. Probe alternate TLDs (company.engineering, company.dev, company.ai)
        alt_tld_sources = self._probe_alternate_tlds(company_name, main_domain)
        discovered.extend(alt_tld_sources)

        # 9. Careers keyword search — find job postings mentioning AI/agent/agentic
        careers_ai_results = self._search_careers_ai_keywords(company_name, main_domain)
        discovered.extend(careers_ai_results)

        # FALLBACK: If we found NOTHING, it might be a search ban or just poor indexing.
        # Story 4.3: Return heuristic candidates for deep crawling.
        if not discovered:
            logger.warning(f"No sources discovered for {company_name}. Using fallback patterns.")
            fallbacks = self._generate_fallback_candidates(main_domain)
            discovered.extend(fallbacks)

        # Story 4.4: Subdomain Discovery (Generic Scanner)
        subdomains = self.discover_subdomains(company_name, main_domain)
        if subdomains:
            discovered.extend(subdomains)

        return discovered

    def discover_subdomains(self, company_name: str, domain: str) -> List[Dict[str, str]]:
        """
        Story 4.4: Systematically scan for high-signal subdomains.
        """
        
        found = []
        # High value prefixes
        prefixes = [
            ("ai", "subdomain_ai"),
            ("research", "subdomain_ai"),
            ("labs", "subdomain_ai"),
            ("engineering", "subdomain_engineering"),
            ("tech", "subdomain_engineering"),
            ("developers", "subdomain_dev"),
            ("developer", "subdomain_dev"),
            ("blog", "engineering_blog"), # often blog.company.com
            ("cloud", "subdomain_cloud"),
            ("gemini", "subdomain_ai"), # Specific but generic enough for now
            ("firebase", "subdomain_dev")
        ]
        
        clean_domain = domain.replace("www.", "")
        
        for prefix, signal_type in prefixes:
            subdomain = f"{prefix}.{clean_domain}"
            url = f"https://{subdomain}"
            
            if self._check_subdomain_exists(url):
                logger.info(f"Discovered Subdomain: {url}")
                found.append({"url": url, "type": signal_type})
                
        return found
        
    def _probe_alternate_tlds(self, company_name: str, domain: str) -> List[Dict[str, str]]:
        """
        Probe alternate TLDs where companies host engineering content.
        e.g., shopify.engineering, google.dev, meta.ai
        """
        # Extract the company/brand portion of the domain (e.g., "shopify" from "shopify.com")
        clean_domain = domain.replace("www.", "")
        brand = clean_domain.split(".")[0]

        alt_tlds = [
            ("engineering", "engineering_blog"),
            ("dev", "subdomain_dev"),
            ("ai", "subdomain_ai"),
            ("tech", "subdomain_engineering"),
        ]

        found = []
        for tld, signal_type in alt_tlds:
            alt_url = f"https://{brand}.{tld}"
            # Skip if it's the same as the main domain
            if f"{brand}.{tld}" == clean_domain:
                continue
            if self._check_subdomain_exists(alt_url):
                logger.info(f"Discovered alternate TLD: {alt_url}")
                found.append({"url": alt_url, "type": signal_type})
        return found

    def _search_careers_ai_keywords(self, company_name: str, domain: str) -> List[Dict[str, str]]:
        """
        Search the company's careers pages for job postings mentioning AI/agent/agentic.
        This surfaces high-signal non-engineering roles without crawling every category.
        """
        clean_domain = domain.replace("www.", "")

        # Keyword search scoped to the company's careers pages
        query = f'site:{clean_domain}/careers ("agentic" OR "AI skills" OR "agent" OR "generative AI" OR "machine learning")'
        found = []
        try:
            results = list(search(query, num_results=5, advanced=True))
            for result in results[:5]:
                url = result.url
                # Skip the main careers landing page itself
                if url.rstrip("/").endswith("/careers"):
                    continue
                found.append({"url": url, "type": "careers_ai_keyword_hit"})
                logger.info(f"Careers AI keyword hit: {result.title} -> {url}")
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "too many" in error_str:
                logger.warning(f"Careers AI keyword search rate-limited for {company_name}")
                self.search_failed = True
            else:
                logger.error(f"Careers AI keyword search failed for {company_name}: {e}")
        return found

    def _check_subdomain_exists(self, url: str) -> bool:
        try:
             # Fast timeout, we just want to know if it responds
             resp = requests.head(url, timeout=2, allow_redirects=True)
             if resp.status_code < 400:
                 return True
             # Some sites block HEAD, try GET
             if resp.status_code == 405: # Method Not Allowed
                 resp = requests.get(url, timeout=2)
                 return resp.status_code < 400
        except:
             return False
        return False

    def _probe_corporate_pages(self, domain: str) -> List[Dict[str, str]]:
        """Probe well-known corporate URL patterns for IR, newsroom, press."""
        clean_domain = domain.replace("www.", "")

        patterns = [
            # Path-based
            (f"https://{clean_domain}/investors", "investor_relations"),
            (f"https://{clean_domain}/investor-relations", "investor_relations"),
            (f"https://{clean_domain}/ir", "investor_relations"),
            (f"https://{clean_domain}/newsroom", "newsroom"),
            (f"https://{clean_domain}/news", "newsroom"),
            (f"https://{clean_domain}/press", "press_release"),
            (f"https://{clean_domain}/press-releases", "press_release"),
            (f"https://{clean_domain}/media", "newsroom"),
            # Subdomain-based
            (f"https://investors.{clean_domain}", "investor_relations"),
            (f"https://newsroom.{clean_domain}", "newsroom"),
            (f"https://press.{clean_domain}", "press_release"),
            (f"https://news.{clean_domain}", "newsroom"),
            (f"https://ir.{clean_domain}", "investor_relations"),
        ]

        seen_types = set()
        found = []
        for url, source_type in patterns:
            if source_type in seen_types:
                continue
            if self._check_subdomain_exists(url):
                logger.info(f"Discovered corporate page: {url} ({source_type})")
                found.append({"url": url, "type": source_type})
                seen_types.add(source_type)
        return found

    def _search_news_articles(self, company_name: str) -> List[Dict[str, str]]:
        """Search for recent news articles about the company and AI."""
        wire_domains = ["businesswire.com", "prnewswire.com", "globenewswire.com"]
        news_domains = ["reuters.com", "techcrunch.com", "venturebeat.com"]
        all_domains = wire_domains + news_domains

        site_filter = " OR ".join(f"site:{d}" for d in all_domains)
        query = f'{company_name} ("artificial intelligence" OR "AI" OR "machine learning") ({site_filter})'

        found = []
        try:
            results = list(search(query, num_results=5, advanced=True))
            for result in results[:3]:
                url = result.url
                if any(d in url for d in wire_domains):
                    found.append({"url": url, "type": "press_release"})
                else:
                    found.append({"url": url, "type": "news_article"})
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "too many" in error_str:
                logger.warning(f"News search rate-limited for {company_name}")
                self.search_failed = True
            else:
                logger.error(f"News search failed for {company_name}: {e}")
        return found

    def _generate_fallback_candidates(self, domain: str) -> List[Dict[str, str]]:
        """Generate standard career URL patterns when search fails."""
        candidates = []
        clean_domain = domain.replace("www.", "")
        
        # Standard paths
        candidates.append({"url": f"https://{clean_domain}/careers", "type": "careers_fallback"})
        candidates.append({"url": f"https://{clean_domain}/jobs", "type": "careers_fallback"})
        candidates.append({"url": f"https://{clean_domain}/about", "type": "about_fallback"})
        
        # Subdomains
        candidates.append({"url": f"https://careers.{clean_domain}", "type": "careers_fallback"})
        
        return candidates

    def extract_ats_links(self, html: str) -> List[str]:
        """Detect ATS providers (Greenhouse, Lever, Ashby, Workday) from HTML.

        Delegates to ATSDetector which scans both anchor tags and iframes.
        """
        return self.ats_detector.extract_ats_links(html)

    def _search_role(self, company: str, role: str, keywords: str) -> Optional[str]:
        # query = f'{company} "{role}" {keywords} job'
        query = f'{company} "{role}" {keywords} job'
        return self._perform_search(query, domain_filter=None, keyword_filter="job")

    def _search_engineering_blog(self, company: str, domain: str) -> Optional[str]:
        query = f'site:{domain} "engineering blog" OR "{company} engineering blog"'
        return self._perform_search(query, domain_filter=None, keyword_filter="blog")

    def _search_github_org(self, company: str) -> Optional[str]:
        query = f'site:github.com "{company}"'
        # We want strict github.com/orgname, avoiding specific repos/issues if possible
        return self._perform_search(query, domain_filter="github.com", keyword_filter=None)

    def _search_careers(self, company: str, domain: str) -> Optional[str]:
        query = f'site:{domain} careers OR "{company} careers" OR "{company} jobs"'
        return self._perform_search(query, domain_filter=None, keyword_filter="careers")

    def _perform_search(self, query: str, domain_filter: Optional[str] = None, keyword_filter: Optional[str] = None) -> Optional[str]:
        try:
            # num_results=3 is usually enough to find the top hit
            results = list(search(query, num_results=3, advanced=True))
            
            for result in results:
                url = result.url
                
                # Check domain filter
                if domain_filter and domain_filter not in url:
                    continue
                    
                # Check keyword filter (simplistic)
                if keyword_filter and keyword_filter.lower() not in url.lower() and keyword_filter.lower() not in result.title.lower():
                     # If generic, maybe perform deeper check? For now, lenient.
                     pass

                return url
                
        except Exception as e:
            error_str = str(e).lower()
            if "429" in error_str or "rate" in error_str or "too many" in error_str:
                logger.warning(f"Search rate-limited (429) for query '{query}'")
                self.search_failed = True
            else:
                logger.error(f"Search failed for query '{query}': {str(e)}")
            return None
        
        return None
