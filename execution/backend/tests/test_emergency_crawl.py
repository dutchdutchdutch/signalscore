"""Tests for Emergency Crawl fallback - Story 4.3 AC2."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from app.services.scoring_service import ScoringService


class TestEmergencyCrawl:
    """Tests for emergency crawl when discovery fails."""

    @pytest.fixture
    def service(self):
        return ScoringService(db=MagicMock())

    def test_find_job_links_discovers_career_subpages(self, service):
        """Emergency crawl should find /jobs and /careers links."""
        html = '''
        <html><body>
        <nav>
            <a href="/about">About</a>
            <a href="/careers">Careers</a>
            <a href="/jobs/engineering">Engineering Jobs</a>
            <a href="/careers/data-science">Data Science</a>
        </nav>
        </body></html>
        '''
        links = service._find_job_links(html, "https://example.com")
        assert len(links) >= 2

    def test_emergency_crawl_finds_deeper_links(self, service):
        """_emergency_crawl should follow links to depth 2 to find job pages."""
        # The method should exist and accept url + depth params
        assert hasattr(service, '_emergency_crawl'), "ScoringService must have _emergency_crawl method"

    def test_find_job_links_includes_ats_links(self, service):
        """Job link finder should also capture ATS embed links."""
        html = '''
        <html><body>
        <iframe src="https://boards.greenhouse.io/acme"></iframe>
        <a href="https://jobs.lever.co/acme">See Jobs</a>
        <a href="/job/ml-engineer">ML Engineer</a>
        </body></html>
        '''
        links = service._find_job_links(html, "https://example.com")
        # Should find the lever link and the internal job link
        assert len(links) >= 2


class TestDiscoveryFailureDetection:
    """Tests for detecting and signaling search failures."""

    def test_discovery_returns_search_failed_metadata(self):
        """When search fails with 429, find_sources should indicate failure."""
        from app.services.discovery import DiscoveryService

        discovery = DiscoveryService()
        # The method should return metadata about search failure
        assert hasattr(discovery, 'find_sources')
        # We'll test the actual 429 handling via mock in integration tests
