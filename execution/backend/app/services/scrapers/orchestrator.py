"""Scraper Orchestrator - dispatches to appropriate strategy."""

import logging
from typing import Optional
from urllib.parse import urlparse

from app.services.scrapers.types import ScraperResult, ScraperConfig, ScraperStrategy
from app.services.scrapers.base import BaseScraper
from app.services.scrapers.generic_html import GenericHtmlScraper
from app.services.scrapers.selenium_scraper import SeleniumScraper

logger = logging.getLogger(__name__)


class ScraperOrchestrator:
    """
    Orchestrates scraping by selecting the appropriate strategy.
    
    Strategy Selection Priority:
    1. Explicit strategy override (if provided)
    2. URL pattern matching (Greenhouse, Lever, etc. → Selenium)
    3. Fallback to Generic HTML
    
    Usage:
        orchestrator = ScraperOrchestrator()
        result = await orchestrator.scrape("https://stripe.com/jobs")
    """
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        self.config = config or ScraperConfig()
        
        # Initialize available strategies (order matters for pattern matching)
        self.strategies: list[BaseScraper] = [
            SeleniumScraper(self.config),  # Check JS-heavy patterns first
            GenericHtmlScraper(self.config),  # Fallback
        ]
    
    async def scrape(
        self,
        url: str,
        force_strategy: Optional[ScraperStrategy] = None,
    ) -> ScraperResult:
        """
        Scrape a URL using the best available strategy.
        
        Args:
            url: The URL to scrape
            force_strategy: Optional strategy override
            
        Returns:
            ScraperResult with content or error details
        """
        logger.info(f"Scraping URL: {url}")
        
        # Validate URL
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return ScraperResult(
                    url=url,
                    success=False,
                    strategy_used=ScraperStrategy.GENERIC_HTML,
                    error_message="Invalid URL format",
                )
        except Exception:
            return ScraperResult(
                url=url,
                success=False,
                strategy_used=ScraperStrategy.GENERIC_HTML,
                error_message="URL parsing failed",
            )
        
        # Select strategy
        scraper = self._select_strategy(url, force_strategy)
        logger.info(f"Selected strategy: {scraper.strategy.value}")
        
        # Execute scrape
        result = await scraper.scrape(url)
        
        # Log outcome
        if result.success:
            logger.info(f"Successfully scraped {url} ({len(result.extracted_text or '')} chars)")
        else:
            logger.warning(f"Failed to scrape {url}: {result.error_message}")
        
        return result
    
    def _select_strategy(
        self,
        url: str,
        force_strategy: Optional[ScraperStrategy] = None,
    ) -> BaseScraper:
        """Select the appropriate scraper strategy."""
        
        # Handle forced strategy
        if force_strategy:
            for strategy in self.strategies:
                if strategy.strategy == force_strategy:
                    return strategy
        
        # Pattern-based selection
        for strategy in self.strategies:
            if strategy.can_handle(url):
                return strategy
        
        # Fallback to generic (should always exist)
        return self.strategies[-1]
    
    async def scrape_batch(
        self,
        urls: list[str],
        force_strategy: Optional[ScraperStrategy] = None,
    ) -> list[ScraperResult]:
        """
        Scrape multiple URLs.
        
        Note: Runs sequentially to respect rate limiting.
        For parallel scraping, implement proper rate limiting first.
        """
        results = []
        for url in urls:
            result = await self.scrape(url, force_strategy)
            results.append(result)
        return results
