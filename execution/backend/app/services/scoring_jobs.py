"""In-memory scoring job registry for tracking background scoring tasks."""

import uuid
from datetime import datetime
from typing import Optional


# Module-level job store. Keys are job IDs, values are job state dicts.
# This is intentionally in-memory — jobs are transient and only matter
# during the scoring lifecycle. Cleared on server restart.
_jobs: dict[str, dict] = {}


def create_job(url: str) -> str:
    """Create a new scoring job and return its ID."""
    job_id = uuid.uuid4().hex[:12]
    _jobs[job_id] = {
        "status": "processing",
        "url": url,
        "company_name": None,
        "error": None,
        "created_at": datetime.now().isoformat(),
    }
    return job_id


def update_job(
    job_id: str,
    status: str,
    company_name: Optional[str] = None,
    error: Optional[str] = None,
) -> None:
    """Update a job's status."""
    if job_id not in _jobs:
        return
    _jobs[job_id]["status"] = status
    if company_name is not None:
        _jobs[job_id]["company_name"] = company_name
    if error is not None:
        _jobs[job_id]["error"] = error


def get_job(job_id: str) -> Optional[dict]:
    """Get a job's current state, or None if not found."""
    return _jobs.get(job_id)
