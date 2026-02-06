
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.models.company import Company, Score
from app.schemas.scores import ScoreResponse, SignalResponse

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

def test_circular_imports_regression():
    """
    Test that importing modules doesn't cause circular import errors.
    This protects against the regression we saw earlier.
    """
    try:
        from app.api.v1.scores import router
        from app.services.scoring_service import ScoringService
        from app.models.company import Company
        assert True
    except ImportError as e:
        pytest.fail(f"Circular import error detected: {e}")

@patch("app.services.scoring_service.ScraperOrchestrator.scrape", new_callable=AsyncMock)
def test_on_demand_scoring_flow(mock_scrape):
    """
    Test the full flow:
    1. POST /scores (Analyze) -> Persist to DB
    2. GET /scores -> Retrieval from DB (Merging logic)
    """
    # Mock Scraper Response
    mock_result = MagicMock()
    mock_result.success = True
    mock_result.extracted_text = "startups using openai and pytorch for autonomous agents"
    mock_scrape.return_value = mock_result

    # 1. Analyze a company
    response = client.post("/api/v1/scores", json={"url": "https://test-startup.com"})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["company_name"] == "Test-startup" # Naive extractor capitalizes
    assert data["score"] > 0
    assert "openai" in data["signals"]["tool_stack"]
    
    # Verify DB persistence directly
    db = TestingSessionLocal()
    company = db.query(Company).filter(Company.name == "Test-startup").first()
    assert company is not None
    assert len(company.scores) == 1
    db.close()

    # 2. List scores (Test GET /scores merging logic)
    response = client.get("/api/v1/scores")
    assert response.status_code == 200
    list_data = response.json()
    
    # Check if "Test-startup" is in the list
    company_names = [c["company_name"] for c in list_data["companies"]]
    assert "Test-startup" in company_names
    
    # Check if Pilot data is also present
    assert "Target" in company_names # Target is in pilot data

def test_invalid_url_validation():
    """
    Test that the API rejects invalid URLs with 422.
    """
    # 1. Plain text (no extension)
    response = client.post("/api/v1/scores", json={"url": "nike"})
    assert response.status_code == 422
    
    # 2. Empty
    response = client.post("/api/v1/scores", json={"url": ""})
    assert response.status_code == 422

def test_get_scores_missing_imports_regression():
    """
    Test GET /scores specifically to catch NameError (e.g. missing 'select').
    """
    response = client.get("/api/v1/scores")
    assert response.status_code == 200
    # If 'select' was missing, this would be 500
