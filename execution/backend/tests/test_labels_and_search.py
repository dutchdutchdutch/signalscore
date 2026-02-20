
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.models.company import Company, Score
from app.models.enums import AIReadinessCategory

# Setup in-memory DB
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

def seed_category_company(db, name, score_val, category):
    """Helper to seed a company with a specific score."""
    company = Company(name=name, domain=f"{name.lower()}.com", careers_url=f"https://{name.lower()}.com")
    db.add(company)
    db.commit()
    
    score = Score(
        company_id=company.id,
        score=score_val,
        category=category,
        signals={
            "ai_keywords": int(score_val),
            "agentic_signals": 0,
            "tool_stack": [],
            "non_eng_ai_roles": 0,
            "has_ai_platform_team": False,
            "jobs_analyzed": 5
        }, # Full Dummy signals
        component_scores={
            "ai_keywords": score_val,
            "agentic_signals": 0.0,
            "tool_stack": 0.0,
            "non_eng_ai": 0.0,
            "ai_platform_team": 0.0
        },
        evidence=[f"Evidence for {category}"]
    )
    db.add(score)
    db.commit()
    return company

def test_api_labels_check_all_categories():
    """
    Store 6 fake companies in the database with a score for each ranking.
    Test API only for all 6.
    """
    db = TestingSessionLocal()
    
    test_cases = [
        ("FakeNoSignal", 0.0, AIReadinessCategory.NO_SIGNAL, "No Signal"),
        ("FakeLagging", 40.0, AIReadinessCategory.LAGGING, "Lagging"),
        ("FakeOperational", 70.0, AIReadinessCategory.OPERATIONAL, "Operational"),
        ("FakeLeading", 90.0, AIReadinessCategory.LEADING, "Leading"),
        ("FakeTransformational", 98.0, AIReadinessCategory.TRANSFORMATIONAL, "Transformational"),
    ]
    
    for name, score, category, expected_label in test_cases:
        seed_category_company(db, name, score, category)
        
    db.close()
    
    # Verify via API
    for name, score, category, expected_label in test_cases:
        # Check Label via POST /scores (simulating lookup)
        resp = client.post("/api/v1/scores", json={"url": f"https://{name.lower()}.com"})
        
        assert resp.status_code == 200, f"Failed for {name}"
        data = resp.json()
        
        assert data["company_name"] == name
        assert data["status"] == "completed"
        # Check label
        assert data["category_label"] == expected_label, f"Label mismatch for {name}. Got {data['category_label']}, expected {expected_label}"
        assert data["score"] == score
        assert data["category"] == category

def test_search_existing_company():
    """Test searching for a stored company finds it."""
    db = TestingSessionLocal()
    company = Company(name="StoredCompany", domain="stored.com", careers_url="https://stored.com")
    db.add(company)
    db.commit()
    db.close()
    
    response = client.get("/api/v1/companies/search?q=Stored")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["name"] == "StoredCompany"

def test_search_non_existent_company():
    """
    Test searching for a fake company not in DB.
    Confirm it's not found. 
    Do not start analysis (GET /search shouldn't start analysis).
    """
    response = client.get("/api/v1/companies/search?q=NoSuchCompany")
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 0
    # Confirmed not found and no analysis started (since it's a GET)
