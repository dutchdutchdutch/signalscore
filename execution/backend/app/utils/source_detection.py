"""
Shared utility functions for source type detection.
Extracted from scoring_service.py and rescore_company.py to avoid duplication (M5 fix).
"""


def detect_source_type(url: str, text: str) -> str:
    """
    Infer source type from URL patterns and text content.
    
    Args:
        url: The source URL
        text: The extracted text content from the URL
        
    Returns:
        Source type string for signal extraction categorization
    """
    url_lower = url.lower()
    text_lower = text.lower()
    
    # Job posting detection
    if any(p in url_lower for p in ['/jobs/', '/careers/', '/job/', 'job-id', 'application', 'jobs/results']):
        # Check for role type in text
        if any(r in text_lower for r in ['product manager', 'product management', 'pm ']):
            return 'product_role'
        elif any(r in text_lower for r in ['marketing', 'growth', 'brand']):
            return 'marketing_role'
        elif any(r in text_lower for r in ['legal', 'counsel', 'attorney', 'compliance']):
            return 'legal_role'
        else:
            return 'job_posting'
    
    # Blog detection
    if 'blog' in url_lower or 'developers' in url_lower:
        return 'engineering_blog'
    
    # GitHub detection
    if 'github' in url_lower:
        return 'github'
        
    # AI/Research subdomain
    if any(s in url_lower for s in ['ai.', 'research.', 'labs.', 'ml.']):
        return 'subdomain_ai'
    
    return 'manual_rescore'
