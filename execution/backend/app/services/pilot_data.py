"""
Pilot Data Service - Load and score pre-computed pilot company data.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from .scoring import ScoreCalculator, SignalData, CompanyScore


# Path to pilot data
PILOT_DATA_PATH = Path(__file__).parent.parent / "data" / "pilot_scores.json"


def load_pilot_data() -> Dict:
    """Load pilot company data from JSON file."""
    if not PILOT_DATA_PATH.exists():
        return {"pilot_companies": [], "metadata": {}}
    
    with open(PILOT_DATA_PATH) as f:
        return json.load(f)


def get_pilot_scores() -> List[CompanyScore]:
    """Get calculated scores for all pilot companies."""
    data = load_pilot_data()
    calculator = ScoreCalculator()
    scores = []
    
    for company_data in data.get("pilot_companies", []):
        signals_raw = company_data.get("signals", {})
        
        signals = SignalData(
            ai_keywords=signals_raw.get("ai_keywords", 0),
            agentic_signals=signals_raw.get("agentic_signals", 0),
            tool_stack=signals_raw.get("tool_stack", []),
            non_eng_ai_roles=signals_raw.get("non_eng_ai_roles", 0),
            has_ai_platform_team=signals_raw.get("has_ai_platform_team", False),
            jobs_analyzed=signals_raw.get("jobs_analyzed", 0),
            sample_quotes=company_data.get("evidence", []),
        )
        
        score = calculator.calculate(company_data["company_name"], signals)
        # Override evidence and add URL
        score.evidence = company_data.get("evidence", [])
        score.careers_url = company_data.get("careers_url")
        scores.append(score)
    
    # Sort by score descending
    scores.sort(key=lambda s: s.score, reverse=True)
    
    return scores


def get_company_score(company_name: str) -> Optional[CompanyScore]:
    """Get score for a specific pilot company."""
    scores = get_pilot_scores()
    for score in scores:
        if score.company_name.lower() == company_name.lower():
            return score
    return None


def get_pilot_companies_summary() -> List[Dict]:
    """Get summary of all pilot companies for API response."""
    scores = get_pilot_scores()
    return [score.to_dict() for score in scores]
