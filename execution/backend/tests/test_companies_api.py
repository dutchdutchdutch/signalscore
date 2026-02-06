"""Tests for the Companies API endpoints."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.models import Company


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_db():
    """Create fresh test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db):
    """Create test client with overridden database."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_companies(test_db):
    """Create sample companies in the database."""
    db = TestingSessionLocal()
    companies = [
        Company(name="Stripe", url="https://stripe.com"),
        Company(name="Shopify", url="https://shopify.com"),
        Company(name="GitHub", url="https://github.com"),
        Company(name="OpenAI", url="https://openai.com"),
    ]
    db.add_all(companies)
    db.commit()
    for c in companies:
        db.refresh(c)
    db.close()
    return companies


class TestSearchEndpoint:
    """Tests for GET /api/v1/companies/search"""

    def test_search_by_name(self, client, sample_companies):
        """Search should find companies by name."""
        response = client.get("/api/v1/companies/search", params={"q": "Stripe"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Stripe"

    def test_search_partial_match(self, client, sample_companies):
        """Search should support partial matching."""
        response = client.get("/api/v1/companies/search", params={"q": "shop"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Shopify"

    def test_search_by_url(self, client, sample_companies):
        """Search should find companies by URL."""
        response = client.get("/api/v1/companies/search", params={"q": "github.com"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "GitHub"

    def test_search_no_results(self, client, sample_companies):
        """Search should return empty array when no matches."""
        response = client.get("/api/v1/companies/search", params={"q": "NonExistentCorp"})
        
        assert response.status_code == 200
        data = response.json()
        assert data == []

    def test_search_case_insensitive(self, client, sample_companies):
        """Search should be case-insensitive."""
        response = client.get("/api/v1/companies/search", params={"q": "OPENAI"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "OpenAI"

    def test_search_camelcase_response(self, client, sample_companies):
        """Response should use camelCase field names."""
        response = client.get("/api/v1/companies/search", params={"q": "Stripe"})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        
        # Check camelCase keys
        company = data[0]
        assert "createdAt" in company
        assert "updatedAt" in company
        assert "created_at" not in company
        assert "updated_at" not in company

    def test_search_requires_query(self, client):
        """Search should require 'q' parameter."""
        response = client.get("/api/v1/companies/search")
        
        assert response.status_code == 422  # Validation error


class TestGetCompanyEndpoint:
    """Tests for GET /api/v1/companies/{id}"""

    def test_get_existing_company(self, client, sample_companies):
        """Should return company by ID."""
        response = client.get(f"/api/v1/companies/{sample_companies[0].id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Stripe"

    def test_get_nonexistent_company(self, client, test_db):
        """Should return 404 for unknown ID."""
        response = client.get("/api/v1/companies/99999")
        
        assert response.status_code == 404


class TestCreateCompanyEndpoint:
    """Tests for POST /api/v1/companies"""

    def test_create_company(self, client, test_db):
        """Should create a new company."""
        response = client.post(
            "/api/v1/companies",
            json={"name": "NewCo", "url": "https://newco.com"},
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "NewCo"
        assert data["url"] == "https://newco.com"
        assert "id" in data
        assert "createdAt" in data

    def test_create_duplicate_company(self, client, sample_companies):
        """Should reject duplicate company names."""
        response = client.post(
            "/api/v1/companies",
            json={"name": "Stripe", "url": "https://different.com"},
        )
        
        assert response.status_code == 409


class TestListCompaniesEndpoint:
    """Tests for GET /api/v1/companies"""

    def test_list_companies(self, client, sample_companies):
        """Should list all companies."""
        response = client.get("/api/v1/companies")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 4

    def test_list_with_pagination(self, client, sample_companies):
        """Should support pagination."""
        response = client.get("/api/v1/companies", params={"limit": 2, "offset": 0})
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
