"""Database-backed scoring job registry for tracking background scoring tasks.

Each function manages its own DB session so job updates are independent of
the scoring task's session — progress persists even if the main task rolls back.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import SessionLocal
from app.models.scoring_job import ScoringJob

# Override for testing — set to a test sessionmaker to redirect DB calls
_session_factory = None


def _get_session():
    return (_session_factory or SessionLocal)()


def create_job(url: str, is_new_company: bool = False) -> str:
    """Create a new scoring job and return its ID."""
    job_id = uuid.uuid4().hex[:12]
    db = _get_session()
    try:
        job = ScoringJob(id=job_id, url=url, status="processing", is_new_company=is_new_company)
        db.add(job)
        db.commit()
    finally:
        db.close()
    return job_id


def can_accept_new_job(is_new_company: bool) -> bool:
    """
    Check if the system can accept a new job based on hourly limits.
    Rescores (is_new_company=False) are always accepted.
    New companies are limited by SCORING_RATE_LIMIT_PER_HOUR.
    """
    if not is_new_company:
        return True

    from app.core.config import settings

    cutoff = datetime.now() - timedelta(hours=1)
    db = _get_session()
    try:
        recent_new_jobs = db.query(ScoringJob).filter(
            ScoringJob.is_new_company == True,
            ScoringJob.created_at > cutoff,
        ).count()
        return recent_new_jobs < settings.SCORING_RATE_LIMIT_PER_HOUR
    finally:
        db.close()


def update_job(
    job_id: str,
    status: str,
    company_name: Optional[str] = None,
    error: Optional[str] = None,
    progress_phase: Optional[str] = None,
    progress_detail: Optional[dict] = None,
) -> None:
    """Update a job's status. Uses its own session for independence."""
    db = _get_session()
    try:
        job = db.query(ScoringJob).filter(ScoringJob.id == job_id).first()
        if not job:
            return
        job.status = status
        if company_name is not None:
            job.company_name = company_name
        if error is not None:
            job.error = error
        if progress_phase is not None:
            job.progress_phase = progress_phase
        if progress_detail is not None:
            job.progress_detail = progress_detail
        # Force updated_at even if onupdate doesn't fire for some drivers
        job.updated_at = datetime.now()
        db.commit()
    finally:
        db.close()


def get_job(job_id: str) -> Optional[dict]:
    """Get a job's current state, or None if not found."""
    db = _get_session()
    try:
        job = db.query(ScoringJob).filter(ScoringJob.id == job_id).first()
        if not job:
            return None
        return {
            "status": job.status,
            "url": job.url,
            "company_name": job.company_name,
            "error": job.error,
            "is_new_company": job.is_new_company,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "progress_phase": job.progress_phase,
        }
    finally:
        db.close()
