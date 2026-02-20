"""
AI Readiness Score Calculator.

Calculates weighted scores from extracted signals.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

from .model import (
    AIReadinessCategory,
    SignalWeights,
    DEFAULT_WEIGHTS,
    SIGNAL_CAPS,
    KNOWN_TOOLS,
    CATEGORY_THRESHOLDS,
    get_category,
    get_category_label,
)


@dataclass
class SignalData:
    """Raw signal data extracted from job postings."""
    ai_keywords: int = 0
    agentic_signals: int = 0
    tool_stack: List[str] = field(default_factory=list)
    non_eng_ai_roles: int = 0
    ai_in_it_signals: int = 0
    has_ai_platform_team: bool = False
    is_ai_platform_provider: bool = False
    jobs_analyzed: int = 0
    sample_quotes: List[str] = field(default_factory=list)
    # New fields for Story 4.2
    source_attribution: Dict[str, List[str]] = field(default_factory=dict) # e.g. {"tool_stack": ["GitHub", "Blog"], "ai_keywords": ["Homepage"]}
    marketing_only: bool = False
    
    # Fix 1 & 2: Weighting and Confidence
    weighted_tool_count: float = 0.0
    confidence_score: float = 0.5 # Default low

    # Tiered AI keyword sub-scores
    ai_success_points: int = 0
    ai_plan_points: int = 0
    ai_generic_points: int = 0
    news_sources_found: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ai_keywords": self.ai_keywords,
            "agentic_signals": self.agentic_signals,
            "tool_stack": self.tool_stack,
            "non_eng_ai_roles": self.non_eng_ai_roles,
            "ai_in_it_signals": self.ai_in_it_signals,
            "has_ai_platform_team": self.has_ai_platform_team,
            "is_ai_platform_provider": self.is_ai_platform_provider,
            "jobs_analyzed": self.jobs_analyzed,
            "source_attribution": self.source_attribution,
            "marketing_only": self.marketing_only,
            "confidence_score": self.confidence_score,
            "ai_success_points": self.ai_success_points,
            "ai_plan_points": self.ai_plan_points,
            "ai_generic_points": self.ai_generic_points,
            "news_sources_found": self.news_sources_found,
        }


@dataclass
class CompanyScore:
    """Calculated score for a company."""
    company_name: str
    score: float
    category: AIReadinessCategory
    category_label: str
    signals: SignalData
    component_scores: Dict[str, float] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)
    careers_url: Optional[str] = None
    confidence_score: float = 0.0 # Propagate to top level
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "company_name": self.company_name,
            "score": round(self.score, 1),
            "category": self.category.value,
            "category_label": self.category_label,
            "signals": self.signals.to_dict(),
            "component_scores": {k: round(v, 1) for k, v in self.component_scores.items()},
            "evidence": self.evidence[:5],  # Top 5 evidence items
            "confidence_score": round(self.confidence_score, 2),
        }


class ScoreCalculator:
    """Calculate AI readiness scores from signal data."""
    
    def __init__(self, weights: Optional[SignalWeights] = None):
        self.weights = weights or DEFAULT_WEIGHTS
        if not self.weights.validate():
            raise ValueError("Signal weights must sum to 1.0")
    
    def _normalize(self, value: float, cap: float) -> float:
        """Normalize a value to 0-100 scale with a cap."""
        if cap <= 0:
            return 0.0
        normalized = (value / cap) * 100
        return min(normalized, 100.0)
    
    def calculate(self, company_name: str, signals: SignalData) -> CompanyScore:
        """Calculate weighted score from signals."""
        
        # Normalize each signal to 0-100
        ai_keywords_score = self._normalize(
            signals.ai_keywords, 
            SIGNAL_CAPS["ai_keywords"]
        )
        
        agentic_score = self._normalize(
            signals.agentic_signals,
            SIGNAL_CAPS["agentic_signals"]
        )
        
        # FIX 1: Use weighted tool count if available, else fallback to raw count
        tool_val = signals.weighted_tool_count if signals.weighted_tool_count > 0 else len(signals.tool_stack)
        tool_stack_score = self._normalize(
            tool_val,
            SIGNAL_CAPS["tool_stack"]
        )
        
        non_eng_score = self._normalize(
            signals.non_eng_ai_roles,
            SIGNAL_CAPS["non_eng_ai_roles"]
        )
        
        ai_in_it_score = self._normalize(
            signals.ai_in_it_signals,
            SIGNAL_CAPS["ai_in_it"]
        )
        # Platform team detection acts as a floor boost
        if signals.has_ai_platform_team:
            ai_in_it_score = max(ai_in_it_score, 50.0)

        # FIX 3: Marketing Only Penalty
        if signals.marketing_only:
            # Apply 50% penalty to unverified components
            # We assume keywords and tool stack are less trusted if marketing_only is True
            # Actually, marketing_only logic says "High Keywords on Homepage but NO GitHub". 
            # So Keywords are present but suspect.
            ai_keywords_score *= 0.5
            tool_stack_score *= 0.5
            ai_in_it_score *= 0.5
            # We keep non_eng_score (might be job listings) and agentic_score (might be specific terms)
        
        # Store component scores
        component_scores = {
            "ai_keywords": ai_keywords_score,
            "agentic_signals": agentic_score,
            "tool_stack": tool_stack_score,
            "non_eng_ai": non_eng_score,
            "ai_in_it": ai_in_it_score,
        }
        
        # Apply weights
        weighted_score = (
            ai_keywords_score * self.weights.ai_keywords +
            agentic_score * self.weights.agentic_signals +
            tool_stack_score * self.weights.tool_stack +
            non_eng_score * self.weights.non_eng_ai +
            ai_in_it_score * self.weights.ai_in_it
        )

        # Build base evidence list
        evidence = self._build_evidence(signals)
        
        # --- SIGNAL BOOSTER LOGIC ---

        # 0. AI Platform Provider Override
        # Companies that BUILD and PROVIDE AI tools/platforms to others
        # (e.g., Google AI Studio, Anthropic Claude, OpenAI GPT) are benchmark
        # transformational companies. This overrides the weighted score.
        if signals.is_ai_platform_provider:
            weighted_score = max(weighted_score, 95.0)
            evidence.append("AI Platform Provider: Company builds and provides AI tools/platforms to others")

        # 1. Excellence Boost: Reward spikey profiles
        # If 2+ components are >= 90 (Excellent), add +10 boost
        excellent_components = sum(1 for s in component_scores.values() if s >= 90.0)
        if excellent_components >= 2:
            weighted_score = min(weighted_score + 10.0, 100.0)
            evidence.append(f"Excellence Boost Applied: {excellent_components} components rated >90 (+10 pts)")

        # Determine initial category
        category = get_category(weighted_score)

        # 2. High-Water Mark (The "3 of 5" Rule)
        # If 3+ components are >= 80 (High), ensure at least OPERATIONAL
        high_components = sum(1 for s in component_scores.values() if s >= 80.0)
        if high_components >= 3:
            min_category = AIReadinessCategory.OPERATIONAL
            # If current category is lower than min_category (by threshold), upgrade it
            # Simple check: map category to "rank"
            cat_ranks = {
                AIReadinessCategory.NO_SIGNAL: 0,
                AIReadinessCategory.LAGGING: 1,
                AIReadinessCategory.OPERATIONAL: 2,
                AIReadinessCategory.LEADING: 3,
                AIReadinessCategory.TRANSFORMATIONAL: 4,
            }
            
            if cat_ranks.get(category, -1) < cat_ranks[min_category]:
                category = min_category
                # Also ensure score reflects this floor if it was very low? 
                # Let's just bump score to threshold of that category if it's lower
                weighted_score = max(weighted_score, CATEGORY_THRESHOLDS[min_category])
                evidence.append(f"High-Water Mark Applied: {high_components} components rated >80 (Category Floor: {get_category_label(min_category)})")
        
        return CompanyScore(
            company_name=company_name,
            score=weighted_score,
            category=category,
            category_label=get_category_label(category),
            signals=signals,
            component_scores=component_scores,
            evidence=evidence,
        )
    
    def _build_evidence(self, signals: SignalData) -> List[str]:
        """Build human-readable evidence list."""
        evidence = []
        
        if signals.ai_keywords > 0:
            parts = []
            if signals.ai_success_points > 0:
                parts.append(f"{signals.ai_success_points} success-evidence")
            if signals.ai_plan_points > 0:
                parts.append(f"{signals.ai_plan_points} strategy/plan")
            if signals.ai_generic_points > 0:
                parts.append(f"{signals.ai_generic_points} general-mention")
            tier_detail = f" ({', '.join(parts)})" if parts else ""
            evidence.append(f"{signals.ai_keywords} AI keyword points{tier_detail} across {signals.jobs_analyzed} sources")
        
        if signals.tool_stack:
            tools = ", ".join(signals.tool_stack[:3])
            evidence.append(f"Tool stack: {tools}")
        
        if signals.agentic_signals > 0:
            evidence.append(f"{signals.agentic_signals} agentic/automation signals")
        
        if signals.ai_in_it_signals > 0:
            evidence.append(f"{signals.ai_in_it_signals} AI keywords found in engineering sources")

        if signals.has_ai_platform_team:
            evidence.append("Dedicated AI platform/strategy team detected")

        if signals.is_ai_platform_provider:
            evidence.append("AI Platform Provider: builds and provides AI tools/platforms")

        if signals.non_eng_ai_roles > 0:
            evidence.append(f"{signals.non_eng_ai_roles} AI mentions in non-engineering roles")

        if signals.news_sources_found > 0:
            evidence.append(f"{signals.news_sources_found} news/press/IR sources analyzed")

        # Add sample quotes
        evidence.extend(signals.sample_quotes[:2])
        
        return evidence


def create_score_from_analysis(company_name: str, analysis_data: Dict[str, Any]) -> CompanyScore:
    """Create a CompanyScore from deep analysis results."""
    
    signals = SignalData(
        ai_keywords=analysis_data.get("total_ai_keywords", 0),
        agentic_signals=analysis_data.get("agentic_signals_count", 0),
        tool_stack=analysis_data.get("tools_mentioned", []),
        non_eng_ai_roles=analysis_data.get("non_eng_ai_roles", 0),
        has_ai_platform_team=False,  # Would need title matching
        jobs_analyzed=analysis_data.get("jobs_analyzed", 0),
        sample_quotes=analysis_data.get("sample_quotes", []),
    )
    
    calculator = ScoreCalculator()
    return calculator.calculate(company_name, signals)
