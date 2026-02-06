"""ATS (Applicant Tracking System) detector for career pages.

Story 4.3 AC1: Detect common ATS platforms embedded in career pages.
These are treated as "High Confidence" sources for scoring.
"""

from typing import List
from bs4 import BeautifulSoup


# ATS domain patterns to detect in URLs and iframes
ATS_PATTERNS = [
    "greenhouse.io",
    "boards.greenhouse.io",
    "jobs.lever.co",
    "lever.co",
    "myworkdayjobs.com",
    "myworkday.com",
    "workday.com",
    "jobs.ashby.io",
    "ashby.io",
    "icims.com",
    "smartrecruiters.com",
]


class ATSDetector:
    """Detects ATS (Applicant Tracking System) links in HTML content."""

    def extract_ats_links(self, html: str) -> List[str]:
        """
        Scan HTML for ATS platform links and iframes.

        Returns deduplicated list of ATS URLs found.
        """
        if not html:
            return []

        soup = BeautifulSoup(html, "html.parser")
        found = set()

        # Check anchor tags
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if self.is_ats_url(href):
                found.add(href)

        # Check iframes (common for Greenhouse embeds)
        for iframe in soup.find_all("iframe", src=True):
            src = iframe["src"]
            if self.is_ats_url(src):
                found.add(src)

        return list(found)

    def is_ats_url(self, url: str) -> bool:
        """Check if a URL belongs to a known ATS platform."""
        if not url:
            return False
        url_lower = url.lower()
        return any(pattern in url_lower for pattern in ATS_PATTERNS)
