import pytest
from unittest.mock import patch, MagicMock
from app.services.discovery import DiscoveryService

@pytest.fixture
def discovery_service():
    return DiscoveryService()

def test_discover_subdomains_found(discovery_service):
    """
    Test that discover_subdomains correctly identifies existing subdomains
    and assigns the correct type.
    """
    # Mock requests to return 200 OK for 'ai.example.com' only
    with patch("requests.head") as mock_head:
        def side_effect(url, timeout, allow_redirects):
            if "ai.example.com" in url:
                mock_resp = MagicMock()
                mock_resp.status_code = 200
                return mock_resp
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            return mock_resp
            
        mock_head.side_effect = side_effect
        
        results = discovery_service.discover_subdomains("Example", "example.com")
        
        # Should find exactly one
        assert len(results) == 1
        assert results[0]["url"] == "https://ai.example.com"
        assert results[0]["type"] == "subdomain_ai"

def test_discover_subdomains_fallback_get(discovery_service):
    """
    Test that if HEAD returns 405 (Method Not Allowed), it falls back to GET.
    """
    with patch("requests.head") as mock_head, patch("requests.get") as mock_get:
        # HEAD -> 405
        head_resp = MagicMock()
        head_resp.status_code = 405
        mock_head.return_value = head_resp
        
        # GET -> 200
        get_resp = MagicMock()
        get_resp.status_code = 200
        mock_get.return_value = get_resp
        
        # We only want to test one specific subdomain to keep it simple/fast
        # But the method scans a list. We can patch the class-level list if we want,
        # or just rely on the fact that it iterates.
        
        # Let's just mock one specific call to succeed: 'ai.example.com'
        # The code iterates ALL prefixes.
        
        results = discovery_service.discover_subdomains("Example", "example.com")
        
        # We expect it to try HEAD then GET for each.
        # Since we mocked return_value (not side_effect) for all calls, 
        # it effectively finds ALL prefixes because GET returns 200 for everything.
        # There are 11 prefixes in the code.
        assert len(results) == 11
        assert mock_get.called

def test_discover_subdomains_none(discovery_service):
    """Test when no subdomains exist."""
    with patch("requests.head") as mock_head:
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_head.return_value = mock_resp
        
        results = discovery_service.discover_subdomains("Example", "example.com")
        assert len(results) == 0
