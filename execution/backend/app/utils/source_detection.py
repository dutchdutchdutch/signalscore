"""
Shared utility functions for source type detection.
Extracted from scoring_service.py and rescore_company.py to avoid duplication (M5 fix).
"""

from urllib.parse import urlparse


# Engineering-related TLDs (company.engineering, company.dev, etc.)
_ENGINEERING_TLDS = {'.engineering', '.dev', '.tech'}

# Non-engineering role keywords grouped by department
# Ordered from most specific to least specific to avoid false matches
# (e.g., "brand" in marketing would match a litigation paralegal page about brand protection)
_NON_ENG_ROLE_KEYWORDS = [
    ('legal_role', [
        'legal', 'counsel', 'attorney', 'compliance',
        'litigation', 'paralegal', 'regulatory',
    ]),
    ('operations_role', [
        'revenue operations', 'revops', 'business operations',
        'strategy & operations', 'supply chain', 'logistics',
    ]),
    ('finance_role', [
        'finance', 'financial analyst', 'accounting',
        'fp&a', 'treasury', 'investor relations',
    ]),
    ('hr_role', [
        'human resources', 'people operations', 'talent acquisition',
        'recruiting', 'recruiter', 'learning & development',
    ]),
    ('product_role', [
        'product manager', 'product management', 'product lead',
        'product director', 'product owner',
    ]),
    ('design_role', [
        'design lead', 'design director', 'design manager',
        'ux ', 'ui ', 'user experience', 'user interface',
        'creative director', 'creative operations',
    ]),
    ('sales_role', [
        'sales', 'account executive', 'business development',
        'customer success', 'solutions engineer',
    ]),
    ('marketing_role', [
        'marketing manager', 'marketing director', 'marketing lead',
        'growth manager', 'growth lead', 'brand manager',
        'communications manager', 'content strategist', 'social media',
    ]),
]

# URL path hints that strongly indicate department (checked before text)
_URL_ROLE_HINTS = {
    'legal': 'legal_role',
    'litigation': 'legal_role',
    'paralegal': 'legal_role',
    'counsel': 'legal_role',
    'operations': 'operations_role',
    'revenue': 'operations_role',
    'revops': 'operations_role',
    'finance': 'finance_role',
    'accounting': 'finance_role',
    'design': 'design_role',
    'creative': 'design_role',
    'marketing': 'marketing_role',
    'product-management': 'product_role',
    'product-manager': 'product_role',
    'sales': 'sales_role',
    'talent': 'hr_role',
    'recruiting': 'hr_role',
    'people': 'hr_role',
}


def _is_engineering_tld(url: str) -> bool:
    """Check if the URL uses an engineering-related TLD (e.g., shopify.engineering)."""
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    return any(hostname.endswith(tld) for tld in _ENGINEERING_TLDS)


def _classify_non_eng_role(text_lower: str, url_lower: str = "") -> str:
    """Classify a job posting into a non-eng role type based on URL hints and text content."""
    # Check engineering keywords first — if it's clearly engineering, don't misclassify
    eng_keywords = [
        'software engineer', 'backend engineer', 'frontend engineer',
        'devops', 'sre ', 'site reliability', 'infrastructure engineer',
        'data engineer', 'platform engineer', 'systems engineer',
        'security engineer', 'machine learning engineer', 'ml engineer',
    ]
    if any(k in text_lower for k in eng_keywords):
        return 'job_posting'

    # URL path hints take priority — the URL slug is often the most specific signal
    url_path = urlparse(url_lower).path if url_lower else ""
    for hint, role_type in _URL_ROLE_HINTS.items():
        if hint in url_path:
            return role_type

    # Fall back to text content matching (ordered specific → broad)
    for role_type, keywords in _NON_ENG_ROLE_KEYWORDS:
        if any(k in text_lower for k in keywords):
            return role_type

    return 'job_posting'


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

    # Engineering blog via alternate TLD (company.engineering, company.dev)
    if _is_engineering_tld(url):
        return 'engineering_blog'

    # Job posting detection — then classify by department
    if any(p in url_lower for p in ['/jobs/', '/careers/', '/job/', 'job-id', 'application', 'jobs/results']):
        return _classify_non_eng_role(text_lower, url_lower)

    # Blog detection
    if 'blog' in url_lower or 'developers' in url_lower:
        return 'engineering_blog'

    # GitHub detection
    if 'github' in url_lower:
        return 'github'

    # AI/Research subdomain
    if any(s in url_lower for s in ['ai.', 'research.', 'labs.', 'ml.']):
        return 'subdomain_ai'

    # Press release / wire services
    if any(d in url_lower for d in ['businesswire.com', 'prnewswire.com', 'globenewswire.com']):
        return 'press_release'

    # News articles
    if any(d in url_lower for d in ['reuters.com', 'techcrunch.com', 'venturebeat.com']):
        return 'news_article'

    # Investor relations
    if any(p in url_lower for p in ['/investors', '/investor-relations', '/ir/', 'investors.']):
        return 'investor_relations'

    # Newsroom / press pages
    if any(p in url_lower for p in ['/newsroom', '/news/', '/press', '/media/', 'newsroom.', 'press.', 'news.']):
        return 'newsroom'

    return 'manual_rescore'
