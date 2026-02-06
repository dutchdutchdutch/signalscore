"""Base scraper interface - Strategy Pattern."""

from abc import ABC, abstractmethod
from typing import Optional

from app.services.scrapers.types import ScraperResult, ScraperConfig, ScraperStrategy


class BaseScraper(ABC):
    """Abstract base class for all scraping strategies."""
    
    strategy: ScraperStrategy
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
    
    @abstractmethod
    async def scrape(self, url: str) -> ScraperResult:
        """
        Scrape content from the given URL.
        
        Args:
            url: The URL to scrape
            
        Returns:
            ScraperResult with extracted content or error details
        """
        pass
    
    @abstractmethod
    def can_handle(self, url: str) -> bool:
        """
        Check if this strategy can handle the given URL.
        
        Args:
            url: The URL to check
            
        Returns:
            True if this strategy is appropriate for the URL
        """
        pass
    
    def _extract_text_from_html(self, html: str) -> str:
        """Extract readable text from HTML content."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove script and style elements
        for element in soup(["script", "style", "nav", "footer", "header"]):
            element.decompose()
        
        # Get text and clean whitespace
        text = soup.get_text(separator=" ", strip=True)
        
        # Normalize whitespace
        import re
        text = re.sub(r"\s+", " ", text)
        
        return text.strip()
    
    def _extract_title(self, html: str) -> Optional[str]:
        """Extract page title from HTML."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, "html.parser")
        title_tag = soup.find("title")
        
        return title_tag.get_text(strip=True) if title_tag else None
