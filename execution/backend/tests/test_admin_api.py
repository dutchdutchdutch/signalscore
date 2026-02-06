
import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.core.database import get_db, Base
from app.api.v1.admin import get_failures
from app.models.company import Company, Score
from datetime import datetime

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

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

def test_get_failures_endpoint():
    db_session = TestingSessionLocal()
    # Seed DB with different failure types
    
    # 1. Blocked Company
    c1 = Company(name="BlockedCorp", domain="blocked.com", discovery_trace={"steps": [{"step": "Scrape", "detail": "403 Forbidden"}]})
    db_session.add(c1)
    
    # 2. Ghost Company
    c2 = Company(name="GhostCorp", domain="ghost.com", discovery_trace={"steps": [{"step": "Discovery", "detail": "Found 0 potential sources"}, {"step": "Deep Scrape", "detail": "Deep scraping 0 satellite sources"}]})
    db_session.add(c2)
    
    # 3. Success Company (Should not appear if filtered, but our logic is loose < 15)
    c3 = Company(name="SuccessCorp", domain="success.com")
    db_session.add(c3)
    s3 = Score(company=c3, score=85.0, category="HIGH", signals={}, component_scores={}, evidence=[])
    db_session.add(s3)
    
    db_session.commit()
    
    # Manually attach scores to c1/c2 for completeness check (as empty scores)
    s1 = Score(company=c1, score=0.0, category="NO_SIGNAL", signals={}, component_scores={}, evidence=[])
    db_session.add(s1)
    s2 = Score(company=c2, score=0.0, category="NO_SIGNAL", signals={}, component_scores={}, evidence=[])
    db_session.add(s2)
    db_session.commit()

    # Call API
    response = client.get("/api/v1/admin/failures")
    assert response.status_code == 200
    data = response.json()
    
    # Verify Content
    names = [d["name"] for d in data]
    assert "BlockedCorp" in names
    assert "GhostCorp" in names
    # SuccessCorp logic: code says "score < 15 OR has trace". 
    # SuccessCorp has score 85 and NO trace. So should NOT be there.
    assert "SuccessCorp" not in names
    
    # Verify AC3 Categorization
    blocked = next(d for d in data if d["name"] == "BlockedCorp")
    assert blocked["probable_cause"] == "Blocked"
    
    ghost = next(d for d in data if d["name"] == "GhostCorp")
    assert ghost["probable_cause"] == "Ghost"
