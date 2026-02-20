from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.utils.validators import validate_and_normalize_url

# Response schemas
class SignalResponse(BaseModel):
    ai_keywords: int
    agentic_signals: int
    tool_stack: List[str]
    non_eng_ai_roles: int
    ai_in_it_signals: int = 0
    has_ai_platform_team: bool
    jobs_analyzed: int
    # 4.2 New Fields
    marketing_only: bool = False
    source_attribution: Dict[str, List[str]] = {}
    confidence_score: float = 0.5
    # Tiered AI keyword breakdown
    ai_success_points: int = 0
    ai_plan_points: int = 0
    ai_generic_points: int = 0
    news_sources_found: int = 0


class ComponentScoresResponse(BaseModel):
    ai_keywords: float
    agentic_signals: float
    tool_stack: float
    non_eng_ai: float
    ai_in_it: float


class ScoringStatusResponse(BaseModel):
    """Response when scoring is in progress or failed."""
    status: str
    message: str
    job_id: Optional[str] = None
    company_name: Optional[str] = None
    careers_url: Optional[str] = None
    error: Optional[str] = None

class SourceResponse(BaseModel):
    url: str
    source_type: str

class ScoreResponse(BaseModel):
    """Response when scoring is complete."""
    status: str = "completed"
    company_id: Optional[int] = None
    company_name: str
    careers_url: Optional[str] = None
    score: float
    category: str
    category_label: str
    signals: SignalResponse
    component_scores: ComponentScoresResponse
    evidence: List[str]
    sources: List[SourceResponse] = []
    scored_at: Optional[datetime] = None


class ScoreListResponse(BaseModel):
    companies: List[ScoreResponse]
    count: int


class ScoreRequest(BaseModel):
    """Request model for on-demand scoring."""
    url: str

    @field_validator("url")
    def validate_url(cls, v: str) -> str:
        return validate_and_normalize_url(v)
