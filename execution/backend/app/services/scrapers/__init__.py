"""Scrapers package - Strategy-based web scraping."""

from app.services.scrapers.types import ScraperResult, ScraperConfig, ScraperStrategy
from app.services.scrapers.orchestrator import ScraperOrchestrator
from app.services.scrapers.base import BaseScraper
from app.services.scrapers.generic_html import GenericHtmlScraper
from app.services.scrapers.selenium_scraper import SeleniumScraper
from app.services.scrapers.ats_detector import ATSDetector

__all__ = [
    "ScraperResult",
    "ScraperConfig",
    "ScraperStrategy",
    "ScraperOrchestrator",
    "BaseScraper",
    "GenericHtmlScraper",
    "SeleniumScraper",
    "ATSDetector",
]
