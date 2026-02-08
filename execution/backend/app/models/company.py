"""Company and Score SQLAlchemy models."""

from datetime import datetime
from typing import List, Optional, Any

from sqlalchemy import String, DateTime, func, ForeignKey, Float, JSON, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import AIReadinessCategory


class Company(Base):
    """Company entity - core data model for SignalScore."""

    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    careers_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Story 4.5: Diagnostic log for scraping/discovery decision tree
    discovery_trace: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Relationships
    scores: Mapped[List["Score"]] = relationship(
        back_populates="company", 
        cascade="all, delete-orphan",
        order_by="desc(Score.created_at)"
    )
    
    sources: Mapped[List["CompanySource"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )
    
    # Story 4-8: Cross-domain aliases
    domain_aliases: Mapped[List["CompanyDomainAlias"]] = relationship(
        back_populates="company",
        cascade="all, delete-orphan",
    )

    # Automatic timestamps
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
        return f"<Company(id={self.id}, name='{self.name}')>"


class Score(Base):
    """Historical scores for companies."""
    
    __tablename__ = "scores"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    
    score: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[AIReadinessCategory] = mapped_column(
        SAEnum(AIReadinessCategory), 
        nullable=False
    )
    
    # Storing complex data as JSON
    signals: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    component_scores: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    evidence: Mapped[List[str]] = mapped_column(JSON, nullable=False)
    
    # Relationship
    company: Mapped["Company"] = relationship(back_populates="scores")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Score(id={self.id}, company='{self.company_id}', score={self.score})>"


class CompanySource(Base):
    """Persistent source URLs for a company."""
    __tablename__ = "company_sources"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False) # storing enum as string
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Story 5-7: User Submissions
    verification_status: Mapped[str] = mapped_column(
        String(20), 
        default="verified", # Default to verified for backward compatibility/scraped sources
        nullable=False
    )
    submitted_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    company: Mapped["Company"] = relationship(back_populates="sources")
    
    last_scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<CompanySource(id={self.id}, url='{self.url}')>"


class CompanyDomainAlias(Base):
    """
    Story 4-8: Cross-domain alias mapping.
    Maps alternative domains (e.g., google.dev, withgoogle.com) to parent company.
    """
    __tablename__ = "company_domain_aliases"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)
    
    alias_domain: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    
    company: Mapped["Company"] = relationship(back_populates="domain_aliases")
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<CompanyDomainAlias(id={self.id}, alias='{self.alias_domain}', company_id={self.company_id})>"
