from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.company import Company, Score
from app.models.enums import AIReadinessCategory
import pytest

client = TestClient(app)

@pytest.fixture
def clean_google():
    """Ensure Google is clean before and after test."""
    db = SessionLocal()
    company = db.query(Company).filter(Company.name == "GoogleTest").first()
    if company:
        db.delete(company)
        db.commit()
    db.close()
    yield
    # Cleanup matches setup
    db = SessionLocal()
    company = db.query(Company).filter(Company.name == "GoogleTest").first()
    if company:
        db.delete(company)
        db.commit()
    db.close()

def test_google_scenario_api(clean_google):
    """
    Regression test for 'Google' API retrieval.
    Ensures that a company named 'Google' (simulated here as GoogleTest)
    with a valid score returns 200 OK and not 500.
    """
    # 1. Seed Data manually to ensure valid state
    db = SessionLocal()
    company = Company(
        name="GoogleTest", 
        domain="google-test.com", 
        careers_url="https://test.google.com",
        url="https://test.google.com"
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    
    score = Score(
        company_id=company.id,
        score=85.0,
        category=AIReadinessCategory.LEADING,
        signals={
            "ai_keywords": 30,
            "agentic_signals": 10,
            "tool_stack": ["pytroch", "tensorflow"],
            "non_eng_ai_roles": 5,
            "has_ai_platform_team": True,
            "jobs_analyzed": 10
        },
        component_scores={
            "ai_keywords": 100.0,
            "agentic_signals": 80.0,
            "tool_stack": 100.0,
            "non_eng_ai": 100.0,
            "ai_platform_team": 100.0
        },
        evidence=["Evidence 1"]
    )
    db.add(score)
    db.commit()
    db.close()
    
    # 2. Query API
    response = client.get("/api/v1/scores/GoogleTest")
    
    # 3. Assert
    assert response.status_code == 200, f"API returned {response.status_code}: {response.text}"
    data = response.json()
    assert data["company_name"] == "GoogleTest"
    assert data["score"] == 85.0
    assert data["category"] == "leading"
