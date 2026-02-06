
import pytest
from app.services.scoring_service import ScoringService
from app.models.company import Company
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base

# Setup In-Memory DB for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_domain_rollup(db):
    service = ScoringService(db)
    
    # 1. Create company via one subdomain
    c1 = service._get_or_create_company("Google", "", "https://xyz.google.com")
    assert c1.domain == "google.com"
    assert c1.id is not None
    c1_id = c1.id

    # 2. Access same company via different subdomain/path
    c2 = service._get_or_create_company("Google", "", "https://www.google.com/hackathon")
    assert c2.id == c1_id
    assert c2.domain == "google.com"
    
    # 3. Access via complex TLD
    c3 = service._get_or_create_company("Yahoo", "", "https://sub.yahoo.co.uk")
    assert c3.domain == "yahoo.co.uk"
    
    # 4. Access via root matches existing
    c4 = service._get_or_create_company("Yahoo", "", "https://yahoo.co.uk/jobs")
    assert c4.id == c3.id
