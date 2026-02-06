"""Tests for JD weighting and section parsing - Story 4.3 AC3."""

import pytest
from app.services.scoring_service import ScoringService
from app.services.scoring.calculator import ScoreCalculator
from unittest.mock import MagicMock


class TestJDWeighting:
    """Tests for job_posting weight boost (AC3)."""

    @pytest.fixture
    def service(self):
        return ScoringService(db=MagicMock())

    def test_job_posting_weight_higher_than_homepage(self, service):
        """PyTorch in a JD should count more than PyTorch on homepage."""
        signals_homepage = service._extract_signals_heuristically({
            "homepage": "We use PyTorch for deep learning."
        })
        signals_jd = service._extract_signals_heuristically({
            "job_posting": "We use PyTorch for deep learning."
        })

        # JD weight (2.0) should be higher than homepage (0.5)
        assert signals_jd.weighted_tool_count > signals_homepage.weighted_tool_count
        assert signals_jd.weighted_tool_count == 2.0  # PyTorch at weight 2.0
        assert signals_homepage.weighted_tool_count == 0.5  # PyTorch at weight 0.5

    def test_jd_tools_resolve_marketing_only(self, service):
        """Finding tools in JDs should prevent marketing_only flag."""
        text_segments = {
            "homepage": "We are an AI company using Machine Learning and Deep Learning. Generative AI LLM NLP Computer Vision.",
            "job_posting": "Required: PyTorch, TensorFlow experience."
        }
        signals = service._extract_signals_heuristically(text_segments)

        # job_posting is now in eng_sources, so marketing_only should be False
        assert signals.marketing_only is False
        assert "pytorch" in signals.tool_stack
        assert "tensorflow" in signals.tool_stack

    def test_jd_only_produces_meaningful_score(self, service):
        """Multiple JDs from a careers crawl should produce score > 40 (AC4)."""
        calc = ScoreCalculator()

        # Simulate crawling 3 JDs from a leading AI company's careers page
        text_segments = {
            "homepage": "Join our team. We're building the future with AI.",
            "job_posting": """
            Senior ML Engineer - Requirements:
            - 5+ years experience with PyTorch or TensorFlow
            - Experience with LLM fine-tuning and deployment
            - Familiarity with Kubernetes and AWS
            - Experience building autonomous agent systems
            - Knowledge of LangChain or similar orchestration frameworks
            We are an AI-first company using machine learning and deep learning.

            Staff Data Scientist - About the team:
            Our AI platform team builds machine learning infrastructure.
            Requirements:
            - Deep expertise in machine learning and data science
            - Experience with Databricks, Snowflake, and OpenAI APIs
            - Agentic workflow design and orchestration
            - NLP and generative AI experience
            This role is part of our AI platform organization.

            Product Manager, AI - Requirements:
            - Experience with artificial intelligence product strategy
            - Understanding of LLM capabilities and generative AI
            - Work with engineering to ship AI-powered features
            - Computer vision or NLP background preferred
            """
        }
        signals = service._extract_signals_heuristically(text_segments)
        result = calc.calculate("TestCo", signals)

        # Should score > 40 (AC4 threshold) with multiple rich JDs
        assert result.score > 40.0, f"Score {result.score} should be > 40 with multiple JDs"

    def test_required_skills_section_boost(self, service):
        """Tools in 'Requirements' sections should get boosted weight."""
        text_segments = {
            "job_posting": """
            About the company: We build great products.

            Requirements:
            - PyTorch expertise required
            - Experience with OpenAI APIs
            - Kubernetes deployment experience

            About the team:
            Our team builds AI-powered solutions.
            """
        }
        signals = service._extract_signals_heuristically(text_segments)

        # Should detect tools from requirements section
        assert "pytorch" in signals.tool_stack
        assert "openai" in signals.tool_stack
        assert "kubernetes" in signals.tool_stack
        # Weight should be 2.0 per tool (JD source weight)
        assert signals.weighted_tool_count >= 6.0  # 3 tools x 2.0 weight
