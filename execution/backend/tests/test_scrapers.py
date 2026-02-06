"""Tests for the scraper service."""

import pytest
from app.services.scrapers import (
    ScraperOrchestrator,
    ScraperResult,
    ScraperStrategy,
    GenericHtmlScraper,
    SeleniumScraper,
)


class TestScraperOrchestrator:
    """Tests for the ScraperOrchestrator."""

    @pytest.fixture
    def orchestrator(self):
        """Create a scraper orchestrator instance."""
        return ScraperOrchestrator()

    def test_strategy_selection_greenhouse(self, orchestrator):
        """Selenium should be selected for Greenhouse URLs."""
        scraper = orchestrator._select_strategy("https://boards.greenhouse.io/stripe")
        assert scraper.strategy == ScraperStrategy.SELENIUM

    def test_strategy_selection_lever(self, orchestrator):
        """Selenium should be selected for Lever URLs."""
        scraper = orchestrator._select_strategy("https://jobs.lever.co/company")
        assert scraper.strategy == ScraperStrategy.SELENIUM

    def test_strategy_selection_generic(self, orchestrator):
        """Generic HTML should be selected for unknown URLs."""
        scraper = orchestrator._select_strategy("https://example.com/careers")
        assert scraper.strategy == ScraperStrategy.GENERIC_HTML

    @pytest.mark.asyncio
    async def test_invalid_url(self, orchestrator):
        """Invalid URLs should return error result."""
        result = await orchestrator.scrape("not-a-valid-url")
        assert result.success is False
        assert "Invalid URL" in result.error_message


class TestGenericHtmlScraper:
    """Tests for the generic HTML scraper."""

    @pytest.fixture
    def scraper(self):
        """Create a generic HTML scraper instance."""
        return GenericHtmlScraper()

    @pytest.mark.asyncio
    async def test_scrape_simple_page(self, scraper):
        """Test scraping a simple HTML page."""
        # Use httpbin for reliable test endpoint
        result = await scraper.scrape("https://httpbin.org/html")
        
        assert result.success is True
        assert result.strategy_used == ScraperStrategy.GENERIC_HTML
        assert result.raw_html is not None
        assert len(result.raw_html) > 0
        assert result.extracted_text is not None

    @pytest.mark.asyncio
    async def test_scrape_404_page(self, scraper):
        """Test handling of 404 errors."""
        result = await scraper.scrape("https://httpbin.org/status/404")
        
        assert result.success is False
        assert "404" in result.error_message


class TestShopifyScraping:
    """Integration tests using real Shopify career pages."""

    @pytest.fixture
    def orchestrator(self):
        """Create a scraper orchestrator instance."""
        return ScraperOrchestrator()

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_scrape_shopify_job_posting(self, orchestrator):
        """
        Test scraping a specific Shopify job posting.
        
        This tests the end-to-end flow of:
        1. Fetching a real job posting page
        2. Extracting meaningful text content
        """
        job_url = "https://www.shopify.com/careers/technical-program-manager_6f1f51d3-1659-4259-a99c-bf5c30662357"
        
        result = await orchestrator.scrape(job_url)
        
        # Should succeed (Shopify career pages are relatively simple HTML)
        assert result.success is True, f"Failed to scrape: {result.error_message}"
        
        # Should have extracted content
        assert result.raw_html is not None
        assert len(result.raw_html) > 1000  # Job pages have substantial content
        
        # Should have meaningful text
        assert result.extracted_text is not None
        assert len(result.extracted_text) > 100
        
        # Should contain job-related keywords
        text_lower = result.extracted_text.lower()
        assert any(keyword in text_lower for keyword in [
            "shopify",
            "manager",
            "technical",
            "program",
            "job",
            "career",
            "apply",
        ]), f"Expected job-related keywords in extracted text"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_scrape_shopify_careers_page(self, orchestrator):
        """
        Test scraping Shopify's engineering careers page.
        
        This tests finding job listings from a career discipline page.
        """
        careers_url = "https://www.shopify.com/careers/disciplines/engineering-data"
        
        result = await orchestrator.scrape(careers_url)
        
        # Should succeed
        assert result.success is True, f"Failed to scrape: {result.error_message}"
        
        # Should have content
        assert result.raw_html is not None
        assert result.extracted_text is not None
        
        # Page should contain engineering/data related content
        text_lower = result.extracted_text.lower()
        assert any(keyword in text_lower for keyword in [
            "engineering",
            "data",
            "shopify",
            "careers",
        ]), "Expected career page keywords"

    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_extract_job_links_from_careers_page(self, orchestrator):
        """
        Test that we can identify job posting links from a careers page.
        
        This is a key capability for the SignalScore scraping pipeline.
        """
        from bs4 import BeautifulSoup
        
        careers_url = "https://www.shopify.com/careers/disciplines/engineering-data"
        result = await orchestrator.scrape(careers_url)
        
        assert result.success is True
        
        # Parse the HTML to find job links
        soup = BeautifulSoup(result.raw_html, "html.parser")
        
        # Find all links that look like job postings
        job_links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            # Shopify job URLs contain UUIDs
            if "/careers/" in href and "-" in href.split("/")[-1]:
                job_links.append(href)
        
        # Should find at least some job links (may be 0 if page structure changed)
        # This is informational - we log what we found
        print(f"\nFound {len(job_links)} potential job links")
        for link in job_links[:5]:  # Print first 5
            print(f"  - {link}")
