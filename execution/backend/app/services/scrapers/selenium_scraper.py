"""Selenium-based scraper for JS-heavy sites.

Based on proven patterns from hyroxcoursecorrect project.
Best for dynamic career pages, SPAs, and ATS embeds.
"""

import asyncio
from typing import Optional
from urllib.parse import urlparse

from app.services.scrapers.base import BaseScraper
from app.services.scrapers.types import ScraperResult, ScraperConfig, ScraperStrategy


class SeleniumScraper(BaseScraper):
    """
    Selenium-based scraper for JavaScript-heavy pages.
    
    Best for:
    - Single Page Applications (SPAs)
    - Greenhouse/Lever ATS embeds
    - Pages requiring JS execution
    - Dynamic content loading
    
    Note: Requires selenium and webdriver-manager in dependencies.
    """
    
    strategy = ScraperStrategy.SELENIUM
    
    # Patterns that strongly suggest Selenium is needed
    JS_HEAVY_PATTERNS = [
        "greenhouse.io",
        "boards.greenhouse.io",
        "jobs.lever.co",
        "workday.com",
        "myworkday",
        "icims.com",
        "smartrecruiters.com",
        "ashby.io",
        "jobs.ashby.io",
    ]
    
    def can_handle(self, url: str) -> bool:
        """Check if URL matches known JS-heavy patterns."""
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in self.JS_HEAVY_PATTERNS)
    
    async def scrape(self, url: str) -> ScraperResult:
        """
        Scrape using Selenium WebDriver.
        
        Runs in a thread pool to avoid blocking async event loop.
        """
        try:
            # Run Selenium in thread pool (it's synchronous)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._scrape_sync,
                url,
            )
            return result
            
        except Exception as e:
            return ScraperResult(
                url=url,
                success=False,
                strategy_used=self.strategy,
                error_message=f"Selenium error: {str(e)}",
            )
    
    def _scrape_sync(self, url: str) -> ScraperResult:
        """Synchronous Selenium scraping logic."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager
        except ImportError:
            return ScraperResult(
                url=url,
                success=False,
                strategy_used=self.strategy,
                error_message="Selenium dependencies not installed. Run: pip install selenium webdriver-manager",
            )
        
        driver = None
        try:
            # Configure Chrome options
            options = Options()
            if self.config.headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument(f"--user-agent={self.config.user_agent}")
            
            # Initialize driver with auto-managed ChromeDriver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(self.config.timeout_seconds)
            
            # Navigate to URL
            driver.get(url)
            
            # Wait for body to be present (basic page load)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for JS content to render
            # This is crucial for SPAs
            import time
            time.sleep(2)
            
            # Get page source after JS execution
            html = driver.page_source
            title = driver.title
            
            return ScraperResult(
                url=url,
                success=True,
                strategy_used=self.strategy,
                raw_html=html,
                extracted_text=self._extract_text_from_html(html),
                title=title,
                metadata={
                    "final_url": driver.current_url,
                    "js_rendered": True,
                },
            )
            
        except Exception as e:
            return ScraperResult(
                url=url,
                success=False,
                strategy_used=self.strategy,
                error_message=f"Selenium scrape failed: {str(e)}",
            )
        finally:
            if driver:
                driver.quit()
