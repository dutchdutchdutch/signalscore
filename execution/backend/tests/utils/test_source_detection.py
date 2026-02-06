"""
Unit tests for the detect_source_type utility function.
H1 Fix: Adding dedicated tests for source type detection logic.
"""
import pytest
from app.utils.source_detection import detect_source_type


class TestDetectSourceType:
    """Test cases for source type detection from URLs and text content."""

    def test_product_role_detection(self):
        """Should detect Product Manager job postings."""
        url = "https://careers.google.com/jobs/results/123456"
        text = "Product Manager - AI Applications. Lead product management for ML tools."
        
        result = detect_source_type(url, text)
        
        assert result == "product_role"

    def test_marketing_role_detection(self):
        """Should detect marketing roles."""
        url = "https://company.com/careers/job/789"
        text = "Growth Marketing Manager. Drive brand awareness and marketing campaigns."
        
        result = detect_source_type(url, text)
        
        assert result == "marketing_role"

    def test_legal_role_detection(self):
        """Should detect legal roles."""
        url = "https://company.com/jobs/attorney-position"
        text = "Corporate Counsel needed. Legal compliance and attorney experience required."
        
        result = detect_source_type(url, text)
        
        assert result == "legal_role"

    def test_generic_job_posting(self):
        """Should detect generic job postings without specific role type."""
        url = "https://company.com/careers/software-engineer"
        text = "Software Engineer. Python and JavaScript required."
        
        result = detect_source_type(url, text)
        
        assert result == "job_posting"

    def test_engineering_blog_detection(self):
        """Should detect engineering blogs."""
        url = "https://blog.company.com/ai-infrastructure"
        text = "How we built our AI infrastructure."
        
        result = detect_source_type(url, text)
        
        assert result == "engineering_blog"

    def test_developers_subdomain_detection(self):
        """Should detect developer-focused content."""
        url = "https://developers.company.com/docs"
        text = "API documentation."
        
        result = detect_source_type(url, text)
        
        assert result == "engineering_blog"

    def test_github_detection(self):
        """Should detect GitHub URLs."""
        url = "https://github.com/company/ml-framework"
        text = "Machine learning framework repository."
        
        result = detect_source_type(url, text)
        
        assert result == "github"

    def test_ai_subdomain_detection(self):
        """Should detect AI/research subdomains."""
        test_cases = [
            "https://ai.company.com/research",
            "https://research.company.com/papers",
            "https://labs.company.com/projects",
            "https://ml.company.com/models",
        ]
        
        for url in test_cases:
            result = detect_source_type(url, "Some AI research content.")
            assert result == "subdomain_ai", f"Failed for {url}"

    def test_fallback_to_manual_rescore(self):
        """Should default to manual_rescore for unrecognized URLs."""
        url = "https://company.com/about"
        text = "About our company."
        
        result = detect_source_type(url, text)
        
        assert result == "manual_rescore"

    def test_case_insensitive_url_matching(self):
        """Should match URL patterns case-insensitively."""
        url = "https://Company.com/CAREERS/Jobs/123"
        text = "Product Manager role"
        
        result = detect_source_type(url, text)
        
        assert result == "product_role"

    def test_case_insensitive_text_matching(self):
        """Should match text patterns case-insensitively."""
        url = "https://company.com/jobs/apply"
        text = "PRODUCT MANAGEMENT position available"
        
        result = detect_source_type(url, text)
        
        assert result == "product_role"
