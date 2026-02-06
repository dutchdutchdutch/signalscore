
import re
from urllib.parse import urlparse

def validate_and_normalize_url(url: str) -> str:
    """
    Validates and normalizes a company URL.
    - Requires at least name.extension (e.g. nike.com)
    - Defaults to https:// if no scheme provided.
    
    Args:
        url: The input URL string.
        
    Returns:
        The normalized URL string (e.g. https://nike.com)
        
    Raises:
        ValueError: If the URL is invalid.
    """
    if not url or not url.strip():
        raise ValueError("URL cannot be empty")
        
    url = url.strip()
    
    # 1. Add scheme if missing OR replace http with https
    if url.startswith("http://"):
        url = url.replace("http://", "https://", 1)
    elif not url.startswith("https://"):
        url = "https://" + url
        
    # 2. Parse
    parsed = urlparse(url)
    domain = parsed.netloc
    
    # 3. Minimal validation: name.extension
    # Must have at least one dot, and parts before/after dot must not be empty
    if "." not in domain:
        raise ValueError("Invalid URL: Must be at least name.extension (e.g. nike.com)")
    
    parts = domain.split(".")
    if len(parts) < 2 or not all(p for p in parts):
         raise ValueError("Invalid URL: Domain parts cannot be empty")
         
    # 4. Check for just a dot or valid TLD-like structure?
    # "nike." -> split -> ["nike", ""] -> fails 'all(p)' check above.
    # ".com" -> split -> ["", "com"] -> fails 'all(p)' check above.
    
    return url
