"""Unit tests for ScoreCalculator service."""

import pytest
from app.services.scoring import (
    ScoreCalculator,
    SignalData,
    AIReadinessCategory,
    SignalWeights,
)

@pytest.fixture
def calculator():
    return ScoreCalculator()

def test_calculator_initialization():
    """Test calculator init with defaults."""
    calc = ScoreCalculator()
    assert calc.weights is not None
    assert calc.weights.ai_keywords == 0.15

def test_calculator_custom_weights():
    """Test calculator with custom weights."""
    custom_weights = SignalWeights(
        ai_keywords=0.5,
        agentic_signals=0.5,
        tool_stack=0.0,
        non_eng_ai=0.0,
        ai_in_it=0.0
    )
    calc = ScoreCalculator(weights=custom_weights)
    assert calc.weights.ai_keywords == 0.5

def test_calculator_invalid_weights():
    """Test validation of weights sum."""
    invalid_weights = SignalWeights(ai_keywords=1.0, agentic_signals=1.0)
    # This assumes SignalWeights defaults fill the rest, making sum > 1
    # Actually dataclass defaults apply, so ai_keywords=1.0 + others = > 1.0
    with pytest.raises(ValueError):
        ScoreCalculator(weights=invalid_weights)

def test_calculate_high_score(calculator):
    """Test a high-scoring company (e.g., Nordstrom profile)."""
    signals = SignalData(
        ai_keywords=25,      # Near max (30)
        agentic_signals=10,  # Good (max 15)
        tool_stack=["sagemaker", "vertex"], # 2 tools (max 5)
        non_eng_ai_roles=2, # Some (max 5)
        ai_in_it_signals=10, # Engineering AI keywords
        has_ai_platform_team=True,
        jobs_analyzed=5
    )

    score = calculator.calculate("Nordstrom", signals)

    assert score.company_name == "Nordstrom"
    assert score.score > 40  # With new weights (non_eng_ai=40%, ai_keywords=10%), score shifts
    assert score.category in [AIReadinessCategory.LAGGING, AIReadinessCategory.OPERATIONAL, AIReadinessCategory.LEADING]
    assert any("25 AI keyword points" in e for e in score.evidence)
    assert "Dedicated AI platform/strategy team detected" in score.evidence

def test_calculate_low_score(calculator):
    """Test a low-scoring company (e.g., Stellantis profile)."""
    signals = SignalData(
        ai_keywords=0,
        agentic_signals=1,
        tool_stack=[],
        non_eng_ai_roles=0,
        has_ai_platform_team=False,
        jobs_analyzed=6
    )
    
    score = calculator.calculate("Stellantis", signals)
    
    assert score.score < 20
    assert score.category == AIReadinessCategory.NO_SIGNAL
    assert score.evidence[0].startswith("1 agentic/automation signals") 
    # Logic in calculator uses agentic_signals > 0 for evidenc

def test_normalization_caps(calculator):
    """Test that signals over the cap don't exceed 100% component score."""
    signals = SignalData(
        ai_keywords=100, # Way over cap of 40
        agentic_signals=50,
        tool_stack=["t1", "t2", "t3", "t4", "t5", "t6"],
        non_eng_ai_roles=10,
        ai_in_it_signals=20, # Over cap of 15
        has_ai_platform_team=True
    )

    score = calculator.calculate("SuperAI", signals)

    # All components at 100 + excellence boost = 100
    assert score.score == 100.0
    assert score.component_scores["ai_keywords"] == 100.0

def test_evidence_generation(calculator):
    """Test evidence string generation."""
    signals = SignalData(
        ai_keywords=5,
        tool_stack=["openai"],
        jobs_analyzed=1
    )
    
    score = calculator.calculate("TestCorp", signals)
    evidence = score.evidence
    
    assert any("5 AI keyword points" in e for e in evidence)
    assert any("Tool stack: openai" in e for e in evidence)
