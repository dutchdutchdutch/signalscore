"""Integration tests for Scores API."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

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
    assert data["signals"]["ai_keywords"] == 23

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
