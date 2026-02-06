from pydantic import BaseModel, Field
from typing import Optional

class GroundTruthItem(BaseModel):
    """
    Validation model for ground truth benchmark entries.
    Story 4-7: Ground Truth Benchmarking
    """
    domain: str
    expected_score: float = Field(..., ge=0, le=100)
    tolerance: float = 10.0 # Allow +/- 10 points deviation
    notes: Optional[str] = None
