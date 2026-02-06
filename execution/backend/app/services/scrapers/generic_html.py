"""Generic HTML scraper using BeautifulSoup - lightweight fallback."""

import httpx
from typing import Optional

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.types import ScraperResult, ScraperConfig, ScraperStrategy


class GenericHtmlScraper(BaseScraper):
    """
    Simple HTML scraper using httpx + BeautifulSoup.
    
    Best for:
    - Static HTML pages
    - Simple career pages without heavy JS
    - Fast, lightweight scraping
    """
    
    strategy = ScraperStrategy.GENERIC_HTML
    
    def can_handle(self, url: str) -> bool:
        """Generic scraper can handle any URL as fallback."""
        return True
    
    async def scrape(self, url: str) -> ScraperResult:
        """Scrape using httpx for simple HTTP requests."""
        try:
            async with httpx.AsyncClient(
                timeout=self.config.timeout_seconds,
                follow_redirects=True,
                verify=False,  # Bypass SSL errors for scraping resilience
            ) as client:
                response = await client.get(
                    url,
                    headers={"User-Agent": self.config.user_agent},
                )
                response.raise_for_status()
                
                html = response.text
                
                return ScraperResult(
                    url=url,
                    success=True,
                    strategy_used=self.strategy,
                    raw_html=html,
                    extracted_text=self._extract_text_from_html(html),
                    title=self._extract_title(html),
                    metadata={
                        "status_code": response.status_code,
                        "content_type": response.headers.get("content-type", ""),
                    },
                )
                
        except httpx.TimeoutException:
            return ScraperResult(
                url=url,
                success=False,
                strategy_used=self.strategy,
                error_message=f"Timeout after {self.config.timeout_seconds}s",
            )
        except httpx.HTTPStatusError as e:
            return ScraperResult(
                url=url,
                success=False,
                strategy_used=self.strategy,
                error_message=f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
            )
        except Exception as e:
            return ScraperResult(
                url=url,
                success=False,
                strategy_used=self.strategy,
                error_message=f"Unexpected error: {str(e)}",
            )
