"""Scraper result and base types."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class ScraperStrategy(str, Enum):
    """Available scraping strategies."""
    
    GENERIC_HTML = "generic_html"  # BeautifulSoup for simple HTML
    SELENIUM = "selenium"  # Selenium for JS-heavy sites
    GREENHOUSE = "greenhouse"  # Greenhouse ATS-specific
    LEVER = "lever"  # Lever ATS-specific


@dataclass
class ScraperResult:
    """Result from a scraping operation."""
    
    url: str
    success: bool
    strategy_used: ScraperStrategy
    raw_html: Optional[str] = None
    extracted_text: Optional[str] = None
    title: Optional[str] = None
    error_message: Optional[str] = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)
    metadata: dict = field(default_factory=dict)
    
    @property
    def is_failed(self) -> bool:
        """Check if scrape failed."""
        return not self.success


@dataclass
class ScraperConfig:
    """Configuration for scraper behavior."""
    
    timeout_seconds: int = 30
    respect_robots_txt: bool = True
    cache_duration_hours: int = 24
    user_agent: str = "SignalScore/0.1 (AI Readiness Research)"
    headless: bool = True  # For Selenium
