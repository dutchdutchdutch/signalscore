
import pytest
from app.utils.validators import validate_and_normalize_url

def test_valid_urls_no_scheme():
    assert validate_and_normalize_url("nike.com") == "https://nike.com"
    assert validate_and_normalize_url("tribe.ai") == "https://tribe.ai"
    assert validate_and_normalize_url("a.team") == "https://a.team"

def test_valid_urls_with_scheme():
    assert validate_and_normalize_url("https://google.com") == "https://google.com"
    # STRICT HTTP -> HTTPS enforcement
    assert validate_and_normalize_url("http://legacy.com") == "https://legacy.com"

def test_subdomains():
    assert validate_and_normalize_url("careers.acme.com") == "https://careers.acme.com"
    assert validate_and_normalize_url("engineering.acme.com") == "https://engineering.acme.com"

def test_invalid_inputs():
    with pytest.raises(ValueError):
        validate_and_normalize_url("nike")
    
    with pytest.raises(ValueError):
        validate_and_normalize_url("justtext")
    
    with pytest.raises(ValueError):
        validate_and_normalize_url(".com")
        
    with pytest.raises(ValueError):
        validate_and_normalize_url("company.")
