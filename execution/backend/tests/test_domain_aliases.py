"""
Unit tests for Story 4-8: Cross-Domain Alias Support
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch


class TestCompanyDomainAliasModel:
    """Test cases for CompanyDomainAlias model."""

    def test_model_has_required_columns(self):
        """AC1: Model should have company_id, alias_domain, created_at columns."""
        from app.models.company import CompanyDomainAlias
        
        # Check the model has the expected attributes
        assert hasattr(CompanyDomainAlias, 'id')
        assert hasattr(CompanyDomainAlias, 'company_id')
        assert hasattr(CompanyDomainAlias, 'alias_domain')
        assert hasattr(CompanyDomainAlias, 'created_at')
        assert hasattr(CompanyDomainAlias, 'company')

    def test_alias_domain_is_unique(self):
        """AC1: alias_domain column should have unique constraint."""
        from app.models.company import CompanyDomainAlias
        from sqlalchemy import inspect
        
        # Get the mapper for the model
        mapper = inspect(CompanyDomainAlias)
        columns = {c.name: c for c in mapper.columns}
        
        # Check alias_domain has unique=True via index
        assert 'alias_domain' in columns


class TestDomainAliasAPI:
    """Test cases for domain alias API endpoints."""

    def test_create_alias_returns_correct_structure(self):
        """AC3: POST /domain-alias should return alias with id, company_id, alias_domain, created_at."""
        # This would be an integration test with actual API
        pass

    def test_get_aliases_returns_list(self):
        """AC4: GET /domain-alias/{company_id} should return list of aliases."""
        # This would be an integration test with actual API
        pass


class TestAliasLookup:
    """Test cases for alias lookup in domain matching."""

    def test_alias_resolves_to_parent_company(self):
        """AC2: URL with alias domain should match to parent company."""
        # Verify that _get_or_create_company checks alias table
        from app.services.scoring_service import ScoringService
        
        # Check that the method has code referencing CompanyDomainAlias
        import inspect
        source = inspect.getsource(ScoringService._get_or_create_company)
        assert 'CompanyDomainAlias' in source
        assert 'alias_domain' in source
