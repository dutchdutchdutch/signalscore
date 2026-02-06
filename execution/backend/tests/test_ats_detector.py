"""Tests for ATSDetector - Story 4.3 AC1."""

import pytest
from app.services.scrapers.ats_detector import ATSDetector


class TestATSDetector:
    """Tests for ATS link detection in HTML content."""

    @pytest.fixture
    def detector(self):
        return ATSDetector()

    def test_detect_greenhouse_iframe(self, detector):
        """Should find Greenhouse embed iframes."""
        html = '''
        <html><body>
        <h1>Careers</h1>
        <iframe src="https://boards.greenhouse.io/acmecorp" width="100%"></iframe>
        </body></html>
        '''
        links = detector.extract_ats_links(html)
        assert len(links) >= 1
        assert any("greenhouse.io" in link for link in links)

    def test_detect_greenhouse_link(self, detector):
        """Should find Greenhouse links in anchor tags."""
        html = '''
        <html><body>
        <a href="https://boards.greenhouse.io/acmecorp/jobs/123">Apply Now</a>
        </body></html>
        '''
        links = detector.extract_ats_links(html)
        assert len(links) >= 1
        assert any("greenhouse.io" in link for link in links)

    def test_detect_lever_link(self, detector):
        """Should find Lever job board links."""
        html = '''
        <html><body>
        <a href="https://jobs.lever.co/acmecorp">See all jobs</a>
        </body></html>
        '''
        links = detector.extract_ats_links(html)
        assert len(links) >= 1
        assert any("lever.co" in link for link in links)

    def test_detect_workday_link(self, detector):
        """Should find Workday/MyWorkday links."""
        html = '''
        <html><body>
        <a href="https://acmecorp.wd5.myworkdayjobs.com/careers">View Jobs</a>
        </body></html>
        '''
        links = detector.extract_ats_links(html)
        assert len(links) >= 1
        assert any("myworkday" in link for link in links)

    def test_detect_ashby_link(self, detector):
        """Should find Ashby job board links."""
        html = '''
        <html><body>
        <a href="https://jobs.ashby.io/acmecorp">Open Positions</a>
        </body></html>
        '''
        links = detector.extract_ats_links(html)
        assert len(links) >= 1
        assert any("ashby" in link for link in links)

    def test_no_ats_links(self, detector):
        """Should return empty list when no ATS links found."""
        html = '''
        <html><body>
        <h1>About Us</h1>
        <a href="/about">About</a>
        <a href="/contact">Contact</a>
        </body></html>
        '''
        links = detector.extract_ats_links(html)
        assert len(links) == 0

    def test_deduplicates_links(self, detector):
        """Should not return duplicate ATS links."""
        html = '''
        <html><body>
        <a href="https://boards.greenhouse.io/acme">Jobs</a>
        <a href="https://boards.greenhouse.io/acme">Apply</a>
        <a href="https://boards.greenhouse.io/acme/jobs/123">ML Engineer</a>
        </body></html>
        '''
        links = detector.extract_ats_links(html)
        assert len(links) == len(set(links))

    def test_detect_ats_in_url(self, detector):
        """Should identify ATS URLs directly."""
        assert detector.is_ats_url("https://boards.greenhouse.io/stripe") is True
        assert detector.is_ats_url("https://jobs.lever.co/openai") is True
        assert detector.is_ats_url("https://acme.wd5.myworkdayjobs.com/en") is True
        assert detector.is_ats_url("https://jobs.ashby.io/acme") is True
        assert detector.is_ats_url("https://example.com/careers") is False
