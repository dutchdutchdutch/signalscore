"""Tests for POST /api/v1/companies/{id}/sources"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models import Company, CompanySource
from app.models.enums import VerificationStatus

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db):
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def sample_company(test_db):
    db = TestingSessionLocal()
    c = Company(name="TestCorp", url="https://testcorp.com", domain="testcorp.com")
    db.add(c)
    db.commit()
    db.refresh(c)
    db.close()
    return c

def test_submit_verified_sources(client, sample_company):
    """Submitting same-domain URLs should verify them."""
    response = client.post(
        f"/api/v1/companies/{sample_company.id}/sources",
        json={"urls": ["https://testcorp.com/blog", "https://engineering.testcorp.com"]}
    )
    
    assert response.status_code == 202
    data = response.json()
    assert data["verified_count"] == 2
    assert data["pending_count"] == 0
    assert data["status"] == "processing"

    # Check DB
    db = TestingSessionLocal()
    sources = db.query(CompanySource).filter(CompanySource.company_id == sample_company.id).all()
    assert len(sources) == 2
    # Check verification status by value, as enum comparison sometimes tricky across sessions/pickling
    assert all(s.verification_status == VerificationStatus.VERIFIED or s.verification_status == "verified" for s in sources)
    db.close()

def test_submit_pending_sources(client, sample_company):
    """Submitting cross-domain URLs should be pending."""
    response = client.post(
        f"/api/v1/companies/{sample_company.id}/sources",
        json={"urls": ["https://medium.com/testcorp"]}
    )
    
    assert response.status_code == 202
    data = response.json()
    assert data["verified_count"] == 0
    assert data["pending_count"] == 1
    assert data["status"] == "queued"

    # Check DB
    db = TestingSessionLocal()
    source = db.query(CompanySource).filter(CompanySource.company_id == sample_company.id).first()
    assert source.verification_status == VerificationStatus.PENDING or source.verification_status == "pending"
    db.close()

def test_duplicate_submission(client, sample_company):
    """Should ignore duplicates."""
    url = "https://testcorp.com/dupe"
    # First submit
    client.post(
        f"/api/v1/companies/{sample_company.id}/sources",
        json={"urls": [url]}
    )
    
    # Second submit
    response = client.post(
        f"/api/v1/companies/{sample_company.id}/sources",
        json={"urls": [url]}
    )
    
    assert response.status_code == 202
    data = response.json()
    assert data["verified_count"] == 0 # Ignored so 0 added
    
    # Check DB count
    db = TestingSessionLocal()
    count = db.query(CompanySource).filter(CompanySource.url == url).count()
    assert count == 1
    db.close()

def test_rate_limit(client, sample_company):
    """Should limit pending submissions."""
    # Submit 3 pending sources (1 per request to force rate limit check on 4th req)
    # Note: Logic counts sources, not requests?
    # Logic: pending_count = count_recent_pending_sources. 
    # If I submit 3 distinct pending sources, count is 3. 
    # Next request sees count >= 3.
    
    urls = [f"https://external{i}.com" for i in range(3)]
    for url in urls:
        client.post(
            f"/api/v1/companies/{sample_company.id}/sources",
            json={"urls": [url]}
        )
        
    # 4th attempt should fail
    response = client.post(
        f"/api/v1/companies/{sample_company.id}/sources",
        json={"urls": ["https://external99.com"]}
    )
    
    assert response.status_code == 429
