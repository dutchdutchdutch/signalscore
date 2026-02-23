"""Integration tests for Scores API."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_overrides():
    """Ensure we use the real DB by clearing any overrides from other tests."""
    app.dependency_overrides = {}
    yield
    app.dependency_overrides = {}


def test_list_scores():
    """Test getting all scores."""
    response = client.get("/api/v1/scores")
    assert response.status_code == 200
    data = response.json()
    
    assert "companies" in data
    assert "count" in data
    assert len(data["companies"]) > 0
    assert data["count"] == len(data["companies"])
    
    # Check structure of first result
    first = data["companies"][0]
    assert "company_name" in first
    assert "score" in first
    assert "category" in first
    assert "signals" in first
    assert "evidence" in first

def test_get_specific_company_score():
    """Test getting score for a known pilot company (Nordstrom)."""
    response = client.get("/api/v1/scores/Nordstrom")
    assert response.status_code == 200
    data = response.json()
    
    assert data["company_name"] == "Nordstrom"
    assert data["score"] > 0
    assert "signals" in data
    assert data["signals"]["ai_keywords"] >= 3

def test_get_company_score_case_insensitive():
    """Test getting score with different casing."""
    response = client.get("/api/v1/scores/nordstrom")
    assert response.status_code == 200
    assert response.json()["company_name"] == "Nordstrom"

def test_get_score_not_found():
    """Test getting score for non-existent company."""
    response = client.get("/api/v1/scores/NonExistentCorp")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


from unittest.mock import patch
from app.core.config import settings
from datetime import datetime, timedelta

@patch("app.api.v1.scores.ScoringService.get_latest_score")
@patch("app.api.v1.scores.ScoringService.score_company")
def test_create_score_rate_limit(mock_score_company, mock_latest):
    """Test that we can only submit SCORING_RATE_LIMIT_PER_HOUR new companies."""
    mock_latest.return_value = None  # Always treat as new company
    
    # Import the job store to manipulate/reset it for testing
    from app.services.scoring_jobs import _jobs
    _jobs.clear()

    # Simulate reaching the limit
    limit = settings.SCORING_RATE_LIMIT_PER_HOUR
    for i in range(limit):
        response = client.post("/api/v1/scores", json={"url": f"https://company{i}.com"})
        assert response.status_code == 202

    # The next one should fail with 429
    response = client.post("/api/v1/scores", json={"url": f"https://company999.com"})
    assert response.status_code == 429
    assert "Hourly limit for discovering new companies reached" in response.json()["detail"]

    # Existing companies should bypass the limit
    mock_latest.return_value = {
        "company_name": "Test",
        "score": 50.0,
        "category": "PLAN",
        "category_label": "Started AI Journey",
        "signals": {
            "ai_keywords": 0,
            "agentic_signals": 0,
            "tool_stack": [],
            "non_eng_ai_roles": 0,
            "has_ai_platform_team": False,
            "jobs_analyzed": 0
        },
        "component_scores": {
            "ai_keywords": 0,
            "tool_stack": 0,
            "agentic_signals": 0,
            "engineering_focus": 0,
            "ai_in_it": 0,
            "non_eng_ai": 0,
        },
        "evidence": []
    }
    response = client.post("/api/v1/scores", json={"url": f"https://existing-company.com"})
    assert response.status_code == 200  # Returns existing score instead of 429
