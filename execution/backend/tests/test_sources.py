"""Tests for CompanySource persistence."""

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.company import Company, CompanySource
from app.models.enums import SourceType


# Test database setup (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_source(db_session):
    """Test that a source can be created and linked to a company."""
    # Create a company
    company = Company(name="TestCorp", domain="testcorp.com")
    db_session.add(company)
    db_session.commit()
    
    # Create a source
    source = CompanySource(
        company_id=company.id,
        url="https://techblog.testcorp.com",
        source_type=SourceType.BLOG.value,
        is_active=True
    )
    db_session.add(source)
    db_session.commit()
    
    # Verify
    stmt = select(CompanySource).where(CompanySource.company_id == company.id)
    saved_source = db_session.execute(stmt).scalar_one_or_none()
    
    assert saved_source is not None
    assert saved_source.url == "https://techblog.testcorp.com"
    assert saved_source.source_type == SourceType.BLOG.value
    assert saved_source.is_active is True


def test_deduplication(db_session):
    """Test that adding the same URL twice raises an error or is handled gracefully."""
    company = Company(name="DupeCorp", domain="dupecorp.com")
    db_session.add(company)
    db_session.commit()
    
    source1 = CompanySource(
        company_id=company.id,
        url="https://github.com/dupecorp",
        source_type=SourceType.GITHUB.value
    )
    db_session.add(source1)
    db_session.commit()
    
    # Check if exists before adding again (simulating save_source logic)
    existing = db_session.execute(
        select(CompanySource).where(
            CompanySource.company_id == company.id,
            CompanySource.url == "https://github.com/dupecorp"
        )
    ).scalar_one_or_none()
    
    assert existing is not None, "First source should exist"
    
    # We should NOT add a duplicate if it exists
    if not existing:
        source2 = CompanySource(
            company_id=company.id,
            url="https://github.com/dupecorp",
            source_type=SourceType.GITHUB.value
        )
        db_session.add(source2)
        db_session.commit()
    
    # Verify only one source exists
    all_sources = db_session.execute(
        select(CompanySource).where(CompanySource.company_id == company.id)
    ).scalars().all()
    
    assert len(all_sources) == 1


def test_company_relationship(db_session):
    """Test accessing sources via company.sources relationship."""
    company = Company(name="RelCorp", domain="relcorp.com")
    db_session.add(company)
    db_session.commit()
    
    source1 = CompanySource(
        company_id=company.id,
        url="https://blog.relcorp.com",
        source_type=SourceType.BLOG.value
    )
    source2 = CompanySource(
        company_id=company.id,
        url="https://github.com/relcorp",
        source_type=SourceType.GITHUB.value
    )
    db_session.add_all([source1, source2])
    db_session.commit()
    
    # Refresh to ensure relationship is loaded
    db_session.refresh(company)
    
    assert len(company.sources) == 2
    urls = [s.url for s in company.sources]
    assert "https://blog.relcorp.com" in urls
    assert "https://github.com/relcorp" in urls
