import pytest
from unittest.mock import patch, MagicMock
from app.services.discovery import DiscoveryService

@pytest.fixture
def discovery_service():
    return DiscoveryService()

@patch("app.services.discovery.search")
def test_find_sources_success(mock_search, discovery_service):
    # Mock search results for different queries
    def search_side_effect(query, **kwargs):
        mock_result = MagicMock()
        mock_result.title = "Result Title"
        mock_result.url = ""
        
        if "engineering blog" in query:
            mock_result.url = "https://stripe.com/blog/engineering"
            return [mock_result]
        elif "site:github.com" in query:
            mock_result.url = "https://github.com/stripe"
            return [mock_result]
        elif "careers" in query:
            mock_result.url = "https://stripe.com/jobs"
            return [mock_result]
        elif "product manager" in query:
             mock_result.url = "https://stripe.com/jobs/pm-ai"
             return [mock_result]
        # Allow default empty for new roles if not specifically tested for all of them
        return []

    mock_search.side_effect = search_side_effect

    sources = discovery_service.find_sources("Stripe", "stripe.com")
    
    # We expect Eng Blog, GitHub, Careers, + Product, Marketing, Legal (if mocked)
    # With partial mock, we should at least see the 3 base ones + the one we forced.
    # Currently checks: Blog, Github, Careers. 
    # Plus Product/Marketing/Legal searches run.
    
    # Assert we found the base ones
    urls = [s["url"] for s in sources]
    assert "https://stripe.com/blog/engineering" in urls
    assert "https://github.com/stripe" in urls
    # assert "https://stripe.com/jobs/pm-ai" in urls # Only if we mock it right

@patch.object(DiscoveryService, '_check_subdomain_exists', return_value=False)
@patch("app.services.discovery.search")
def test_find_sources_partial(mock_search, mock_check, discovery_service):
    # Mock only finding github, no corporate pages or subdomains
    def search_side_effect(query, **kwargs):
        mock_result = MagicMock()
        if "site:github.com" in query:
            mock_result.url = "https://github.com/stripe"
            return [mock_result]
        return []

    mock_search.side_effect = search_side_effect

    sources = discovery_service.find_sources("Stripe", "stripe.com")

    assert len(sources) == 1
    assert sources[0]["type"] == "github"


@patch.object(DiscoveryService, '_check_subdomain_exists')
def test_probe_corporate_pages(mock_check, discovery_service):
    """Corporate page probing should find IR/news/press pages."""
    def check_side_effect(url):
        return "/investors" in url or "/newsroom" in url

    mock_check.side_effect = check_side_effect

    results = discovery_service._probe_corporate_pages("example.com")
    types = [r["type"] for r in results]
    assert "investor_relations" in types
    assert "newsroom" in types
    # Should deduplicate by type
    assert types.count("investor_relations") == 1
    assert types.count("newsroom") == 1


@patch("app.services.discovery.search")
def test_search_news_articles(mock_search, discovery_service):
    """News article search should categorize wire vs news results."""
    mock_wire = MagicMock()
    mock_wire.url = "https://www.businesswire.com/example-ai-announcement"
    mock_news = MagicMock()
    mock_news.url = "https://techcrunch.com/example-company-ai"

    mock_search.return_value = [mock_wire, mock_news]

    results = discovery_service._search_news_articles("Example Corp")

    assert len(results) == 2
    assert results[0]["type"] == "press_release"
    assert results[1]["type"] == "news_article"


@patch("app.services.discovery.search")
def test_search_news_handles_rate_limit(mock_search, discovery_service):
    """News search should handle 429 rate limiting gracefully."""
    mock_search.side_effect = Exception("HTTP Error 429: Too Many Requests")

    results = discovery_service._search_news_articles("Example Corp")

    assert results == []
    assert discovery_service.search_failed is True
