
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime

from app.main import app
from app.core.database import get_db, Base
from app.models.company import Company, Score
from app.models.enums import AIReadinessCategory
from app.services.scoring_service import ScoringService
from sqlalchemy import select

# Setup in-memory DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_async_scoring_flow_existing_company():
    """
    Test 1: Existing company returns immediately with status='completed' and score data.
    """
    # Seed DB
    db = TestingSessionLocal()
    company = Company(name="Existing", domain="existing.com", careers_url="https://existing.com")
    db.add(company)
    db.commit()
    
    score = Score(
        company_id=company.id,
        score=85.0,
        category=AIReadinessCategory.LEADING,
        signals={
            "tool_stack": ["openai"],
            "ai_keywords": 10,
            "agentic_signals": 5,
            "non_eng_ai_roles": 0,
            "has_ai_platform_team": True,
            "jobs_analyzed": 10
        },
        component_scores={
            "ai_keywords": 85.0,
            "agentic_signals": 85.0,
            "tool_stack": 85.0,
            "non_eng_ai": 85.0,
            "ai_platform_team": 85.0
        },
        evidence=["Great AI"]
    )
    db.add(score)
    db.commit()
    db.close()

    # Call API
    response = client.post("/api/v1/scores", json={"url": "https://existing.com"})
    
    # Expect 200 OK and data
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["score"] == 85.0
    assert data["company_name"] == "Existing"


@patch("app.services.scoring_service.ScraperOrchestrator.scrape", new_callable=AsyncMock)
def test_async_scoring_flow_new_company(mock_scrape):
    """
    Test 2: New company returns immediately with status='processing'.
    Background task should interpret this (we won't test BG execution here, just response).
    """
    # Call API with new company
    response = client.post("/api/v1/scores", json={"url": "https://new-corp.com"})
    
    # Expect 202 Accepted (or 200 with status=processing)
    # User said "ask user to hang on or come back later", so "Processing" state.
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "processing"
    assert "check back later" in data["message"].lower()

@pytest.mark.asyncio
async def test_score_company_insecure_site_fallback():
    """
    Test 3: If scraper fails (e.g. SSL error), treat as Low Tech signal.
    """
    # Setup
    db = TestingSessionLocal()
    service = ScoringService(db)
    
    # Mock Scraper to fail
    mock_scraper = AsyncMock()
    mock_result = MagicMock()
    mock_result.success = False
    mock_result.error_message = "SSLError: certificate verify failed"
    mock_scraper.scrape.return_value = mock_result
    service.scraper = mock_scraper
    
    # Execution
    await service.score_company("https://insecure.com")
    
    # Verification
    stmt = select(Company).where(Company.domain == "insecure.com")
    company = db.execute(stmt).scalar_one_or_none()
    assert company is not None
    assert len(company.scores) > 0
    score = company.scores[0]
    
    assert score.category == AIReadinessCategory.NO_SIGNAL
    assert score.score == 0.0 # No Signal = 0 score
    assert "No Signal" in str(score.evidence)
    
    db.close()
