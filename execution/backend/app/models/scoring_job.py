"""ScoringJob model for persistent job tracking across instances."""

from datetime import datetime
from typing import Optional, Any

from sqlalchemy import String, DateTime, Boolean, JSON, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ScoringJob(Base):
    """Tracks background scoring jobs in the database.

    Replaces the previous in-memory job dict so that job state
    survives instance restarts and is visible across Cloud Run instances.
    """

    __tablename__ = "scoring_jobs"

    id: Mapped[str] = mapped_column(String(12), primary_key=True)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="processing")
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    error: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    is_new_company: Mapped[bool] = mapped_column(Boolean, default=True)
    progress_phase: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    progress_detail: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ScoringJob(id='{self.id}', status='{self.status}', url='{self.url}')>"
