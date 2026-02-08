from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, Field

from app.models.enums import SourceType, VerificationStatus


class CompanySourceBase(BaseModel):
    """Base schema for CompanySource."""
    url: str
    source_type: SourceType = SourceType.OTHER
    is_active: bool = True


class CompanySourceCreate(CompanySourceBase):
    """Schema for creating a new CompanySource."""
    pass


class CompanySourceSubmission(BaseModel):
    """Schema for user submission of URLs."""
    urls: list[HttpUrl] = Field(..., max_length=3, description="List of up to 3 URLs to submit")


class CompanySourceRead(CompanySourceBase):
    """Schema for reading a CompanySource."""
    id: int
    company_id: int
    verification_status: VerificationStatus
    submitted_by: Optional[str] = None
    last_scraped_at: datetime

    model_config = ConfigDict(from_attributes=True)
