
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base
from app.services.scoring_service import ScoringService
from app.models.company import Company

# Setup in-memory DB
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.mark.asyncio
async def test_scoring_populates_trace():
    """Verify that scoring a company populates the discovery_trace field."""
    db_session = TestingSessionLocal()
    try:
        # 1. Setup Service with Mocks
        service = ScoringService(db_session)
        service.scraper = AsyncMock()
        service.calculator = MagicMock()
        
        # Mock Scraper Results
        mock_result = AsyncMock()
        mock_result.success = True
        mock_result.raw_html = "<html><body><p>AI Company</p></body></html>"
        mock_result.extracted_text = "AI Company working on LLMs."
        service.scraper.scrape.return_value = mock_result
        
        # Mock Calculator
        mock_score = MagicMock()
        mock_score.score = 4.5
        mock_score.category = "LOW"
        mock_score.signals = MagicMock()
        mock_score.signals.to_dict.return_value = {"ai_keywords": 1}
        mock_score.component_scores = {}
        mock_score.evidence = []
        service.calculator.calculate.return_value = mock_score
        
        # 2. Run Scoring
        url = "https://trace-test.com"
        await service.score_company(url)
        
        # 3. Verify Persistence
        company = db_session.query(Company).filter_by(careers_url=url).first()
        assert company is not None
        assert company.discovery_trace is not None
        
        # Verify Trace Structure
        trace = company.discovery_trace
        assert "steps" in trace
        steps = trace["steps"]
        assert len(steps) > 0
        
        # Check for key log entries we added
        step_names = [s["step"] for s in steps]
        print(f"Captured Steps: {step_names}")  # Debug output
        
        assert "Starting scoring" in step_names
        assert "DiscoveryService: Finding sources" in step_names
        assert "Scoring Complete" in step_names

    finally:
        db_session.close()
