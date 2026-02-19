import pytest
from app.services.scoring_service import ScoringService
from app.services.scoring.calculator import SignalData
from unittest.mock import MagicMock

def test_marketing_only_flag():
    """
    Test that if AI terms appear ONLY on homepage, but NOT in engineering sources,
    the marketing_only flag is set.
    """
    service = ScoringService(db=MagicMock())
    
    # 1. Marketing Heavy: Homepage has "artificial intelligence", GitHub has none.
    text_segments = {
        "homepage": "We are an Artificial Intelligence first company using Deep Learning. Our Generative AI and LLM strategy is huge. We love Machine Learning and NLP.",
        "github": "Standard web app with React and Node.",
        "engineering_blog": "How we scaled postgres."
    }
    
    signals = service._extract_signals_heuristically(text_segments)
    
    # Homepage has keywords
    assert "homepage" in signals.source_attribution["ai_keywords"]
    # GitHub does not
    assert "github" not in signals.source_attribution["ai_keywords"]
    # Should be flagged
    assert signals.marketing_only is True

def test_engineering_validation():
    """
    Test that if Engineering sources confirm AI, marketing_only is False.
    """
    service = ScoringService(db=MagicMock())
    
    text_segments = {
        "homepage": "AI Company",
        "github": "Repo using PyTorch and Transformers.",
        "engineering_blog": "Training LLMs on k8s."
    }
    
    signals = service._extract_signals_heuristically(text_segments)
    
    assert "github" in signals.source_attribution["tool_stack"] or "github" in signals.source_attribution["ai_keywords"]
    assert signals.marketing_only is False

def test_non_eng_roles_weighting():
    """
    Test that finding a 'product_role' with 'agentic' keywords boosts non_eng score.
    """
    service = ScoringService(db=MagicMock())
    
    text_segments = {
        "product_role": "We are looking for a Lead Product Manager to drive our Agentic AI roadmap using Orchestration.",
    }
    
    signals = service._extract_signals_heuristically(text_segments)
    
    # Should get points for role type (+2) + keywords (+5) + Lead (+5) = 12?
    # Cap is 15 in code
    assert signals.non_eng_ai_roles >= 10
    assert "product_role" in signals.source_attribution["non_eng_ai_roles"]

def test_tool_stack_weighting():
    """
    Test that tools found on GitHub are worth more than Homepage.
    """
    service = ScoringService(db=MagicMock())
    
    # Case A: Homepage Only
    signals_a = service._extract_signals_heuristically({
        "homepage": "We use PyTorch."
    })
    
    # Case B: GitHub Only
    signals_b = service._extract_signals_heuristically({
        "github": "We use PyTorch."
    })
    
    # PyTorch on GitHub (2.0) should be > Homepage (0.5)
    assert signals_b.weighted_tool_count > signals_a.weighted_tool_count

def test_confidence_score():
    """
    Test that confidence increases with source variety.
    """
    service = ScoringService(db=MagicMock())
    
    # Low Confidence
    s1 = service._extract_signals_heuristically({"homepage": "AI"})
    assert s1.confidence_score == 0.5
    
    # Medium Confidence
    s2 = service._extract_signals_heuristically({"homepage": "AI", "github": "AI"})
    assert s2.confidence_score == 0.8
    
    # High Confidence
    s3 = service._extract_signals_heuristically({"homepage": "AI", "github": "AI", "engineering_blog": "AI"})
    assert s3.confidence_score == 1.0

def test_marketing_penalty_integration():
    """
    Test that marketing_only flag actually reduces the calculated score.
    """
    from app.services.scoring.calculator import ScoreCalculator
    calc = ScoreCalculator()
    
    service = ScoringService(db=MagicMock())
    
    # 1. Marketing Heavy Profile (Should be Penalized)
    # High keywords on Homepage (trigger flag), no tech evidence
    # We populate 'tool_stack' to simulate finding tools in text, but source is homepage
    text_bad = {
        "homepage": "Artificial Intelligence Deep Learning Generative AI LLM. We use PyTorch and Kubernetes." 
    }
    signals_bad = service._extract_signals_heuristically(text_bad)
    # Force flag for test if logic is strict (logic requires keywords > 5 and NO eng sources)
    # The text above has 4 keywords: AI, Deep Learning, Gen AI, LLM. Let's add more.
    text_bad["homepage"] += " Machine Learning NLP Computer Vision."
    signals_bad = service._extract_signals_heuristically(text_bad)
    
    assert signals_bad.marketing_only is True
    score_bad = calc.calculate("Bad Co", signals_bad).score
    
    # 2. Honest Profile (Same content, but verified on GitHub)
    # We use a trick: same text but assigned to 'github' so it counts as verified
    # BUT wait, marketing_only logic says "Homepage has AI AND Eng sources dont".
    # So for Honest profile, we need AI on GitHub.
    text_good = {
        "homepage": "Same text.",
        "github": "Artificial Intelligence Deep Learning Generative AI LLM Machine Learning NLP. We use PyTorch and Kubernetes."
    }
    signals_good = service._extract_signals_heuristically(text_good)
    assert signals_good.marketing_only is False
    score_good = calc.calculate("Good Co", signals_good).score
    
    # The 'Good' score should be significantly higher because:
    # A) No penalty
    # B) Higher weighting for GitHub vs Homepage
    assert score_good > score_bad
    print(f"Bad Score: {score_bad}, Good Score: {score_good}")

def test_verified_job_clears_flag():
    """
    Story 4.3: Finding a verified job description (ATS link) should
    clear the Marketing Only flag, even if homepage is hype-heavy.
    """
    service = ScoringService(db=MagicMock())
    
    # 1. Hype Homepage + ATS Link
    text = {
        "homepage": "We use AI AI AI AI AI AI.", 
        "job_posting_verified": "We require experience with PyTorch and LLMs."
    }
    signals = service._extract_signals_heuristically(text)
    
    assert signals.marketing_only is False # Should be cleared
    assert "pytorch" in signals.tool_stack
    assert signals.weighted_tool_count >= 2.0 # Weight should be High (2.0) for verified job
    
def test_subdomain_boost():
    """
    Story 4.4: Subdomains like ai.company.com should carry high weight (2.0)
    and contribute significantly to the score.
    """
    service = ScoringService(db=MagicMock())

    text = {
        "homepage": "Generic marketing content.",
        "subdomain_ai": "Our AI Research team uses TensorFlow and JAX."
    }
    signals = service._extract_signals_heuristically(text)

    assert "tensorflow" in signals.tool_stack
    # Weight for subdomain_ai is 2.0
    assert signals.weighted_tool_count >= 2.0


def test_tiered_keyword_success_evidence():
    """Success-tier keywords should score higher than generic mentions."""
    service = ScoringService(db=MagicMock())

    # Company A: Generic AI mentions only
    signals_generic = service._extract_signals_heuristically({
        "homepage": "We use artificial intelligence and machine learning."
    })

    # Company B: Concrete AI success evidence
    signals_success = service._extract_signals_heuristically({
        "homepage": "Our AI-powered recommendation engine deployed ai in production. We launched AI features."
    })

    assert signals_success.ai_success_points > 0
    assert signals_success.ai_keywords >= signals_generic.ai_keywords


def test_tiered_keyword_plan_evidence():
    """Plan/strategy keywords should score at medium tier."""
    service = ScoringService(db=MagicMock())

    signals = service._extract_signals_heuristically({
        "investor_relations": "Our AI strategy includes investing in generative AI. We appointed a Chief AI Officer to lead our AI transformation."
    })

    assert signals.ai_plan_points > 0
    assert signals.ai_generic_points > 0  # "generative ai" also matches generic tier
    # "ai strategy" (2) + "ai transformation" (2) + "chief ai officer" (2) = 6,
    # discounted by 0.7 recency multiplier (IR source, no date) → int(6*0.7) = 4
    assert signals.ai_plan_points >= 4


def test_news_source_tracking():
    """News sources should be counted in SignalData."""
    service = ScoringService(db=MagicMock())

    signals = service._extract_signals_heuristically({
        "homepage": "Generic homepage.",
        "news_article": "Company launches AI product.",
        "press_release": "Company announces AI partnership.",
        "investor_relations": "Q4 earnings: AI revenue grew 40%.",
    })

    assert signals.news_sources_found == 3


def test_ir_clears_marketing_flag():
    """AI keywords in IR content should prevent marketing_only flag."""
    service = ScoringService(db=MagicMock())

    signals = service._extract_signals_heuristically({
        "homepage": "We use AI AI AI AI AI AI company using AI everywhere. Machine Learning Deep Learning.",
        "investor_relations": "Our AI strategy is central to our growth. Machine learning drives efficiency."
    })

    # IR content should prevent marketing_only even without eng sources
    assert signals.marketing_only is False


def test_recency_multiplier():
    """Old news content should be discounted via recency multiplier."""
    from app.services.scoring_service import _estimate_recency_multiplier

    # Recent date should get full credit
    recent = _estimate_recency_multiplier("Published January 15, 2026. Company launches AI product.")
    assert recent == 1.0

    # Very old date should get zero
    old = _estimate_recency_multiplier("Published January 15, 2020. Company launches AI product.")
    assert old == 0.0

    # No date should get fallback
    no_date = _estimate_recency_multiplier("Company launches AI product.")
    assert no_date == 0.7
