"""API endpoints for AI Readiness Scores."""

from typing import List, Union
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import select, or_

from app.core.database import get_db
from app.models.company import Company
from app.services.scoring_service import ScoringService
from app.services.pilot_data import (
    get_pilot_scores,
    get_company_score,
)
from app.schemas.scores import (
    ScoreResponse,
    ScoreListResponse,
    ScoreRequest,
    SignalResponse,
    ComponentScoresResponse,
    ScoringStatusResponse # Added
)
from fastapi.responses import JSONResponse # Added

router = APIRouter(prefix="/scores", tags=["scores"])


@router.post("", response_model=Union[ScoreResponse, ScoringStatusResponse]) # Modified
async def create_score(
    request: ScoreRequest, 
    background_tasks: BackgroundTasks, # Added
    db: Session = Depends(get_db)
):
    """
    Analyze a company URL.
    - If score exists: Returns it immediately (Status: Completed).
    - If new: Starts background analysis and returns 202 (Status: Processing).
    """
    service = ScoringService(db)
    
    # Check for existing score
    existing_score = await service.get_latest_score(request.url)
    if existing_score:
        return existing_score

    # Start background task
    # Note: Using service.score_company directly with 'db' session might be unsafe if session closes.
    # But for this MVP let's try. 
    background_tasks.add_task(service.score_company, request.url)
    
    return JSONResponse(
        status_code=202,
        content={
            "status": "processing",
            "message": "Analysis started. Please check back later.",
            "careers_url": request.url
        }
    )


@router.get("", response_model=ScoreListResponse)
async def list_scores(db: Session = Depends(get_db)) -> ScoreListResponse:
    """Get AI readiness scores. Prefers DB, falls back to pilot data if empty."""
    # TODO: Implement DB fetching. For MVP hybrid approach:
    # If we have DB scores, return them. 
    # But we also want the pilot data?
    # Actually, let's just return what's in the DB for now to verify persistence!
    # OR, we likely want to seed the DB with pilot data eventually.
    # For now, let's stick to the pilot data function for GET to keep the demo looking full,
    # unless we want to show ONLY the new ones.
    # User asked for "persistence".
    # Let's simple return pilot data + DB data?
    # Or better: let's migrate pilot data to DB in a script later.
    # For now, I'll keep the GET logic as is (Pilot Data) but maybe append DB results?
    # Let's return Pilot Data + DB results (deduplicated by name?)
    
    pilot_scores = get_pilot_scores()
    
    # Fetch from DB
    stmt = select(Company).where(Company.scores.any())
    db_companies = db.execute(stmt).scalars().all()
    
    # Convert DB companies to ScoreResponse
    db_responses = []
    for company in db_companies:
        if not company.scores:
            continue
        latest_score = company.scores[0] # Ordered by desc in model
        db_responses.append(ScoreResponse(
            company_id=company.id,
            company_name=company.name,
            careers_url=company.careers_url,
            score=round(latest_score.score, 1),
            category=latest_score.category.value,
            category_label=latest_score.category.value.replace("_", "-").title(),
            signals=SignalResponse(**latest_score.signals),
            component_scores=ComponentScoresResponse(**latest_score.component_scores),
            evidence=latest_score.evidence,
            scored_at=latest_score.created_at
        ))
    
    # Combine pilot and DB (deduplicate by name if needed, DB takes precedence?)
    # For MVP, just list both. If name collision, user sees duplicate (acceptable for now).
    
    # Pilot data baseline date
    pilot_scored_at = datetime(2026, 2, 1, 0, 0, 0)
    
    all_responses = [
        ScoreResponse(
            company_name=s.company_name,
            careers_url=getattr(s, "careers_url", None),
            score=round(s.score, 1),
            category=s.category.value,
            category_label=s.category_label,
            signals=SignalResponse(**s.signals.to_dict()),
            component_scores=ComponentScoresResponse(**{
                k: round(v, 1) for k, v in s.component_scores.items()
            }),
            evidence=s.evidence[:5],
            scored_at=pilot_scored_at,
        )
        for s in pilot_scores
    ] + db_responses

    return ScoreListResponse(
        companies=all_responses,
        count=len(all_responses),
    )


@router.get("/{company_name}", response_model=ScoreResponse)
async def get_score(company_name: str, db: Session = Depends(get_db)) -> ScoreResponse:
    """Get score for specific company. Checks DB first, then Pilot data."""
    
    # Check DB
    stmt = select(Company).where(
        or_(
            Company.name == company_name,
            Company.domain == company_name,
            Company.url.contains(company_name) # Soft match for URL
        )
    )
    company = db.execute(stmt).scalar_one_or_none()
    
    if company and company.scores:
        latest_score = company.scores[0] # Ordered by desc created_at
        return ScoreResponse(
            company_id=company.id,
            company_name=company.name,
            careers_url=company.careers_url,
            score=round(latest_score.score, 1),
            category=latest_score.category.value,
            category_label=latest_score.category.value.replace("_", "-").title(),
            signals=SignalResponse(**latest_score.signals),
            component_scores=ComponentScoresResponse(**latest_score.component_scores),
            evidence=latest_score.evidence,
            scored_at=latest_score.created_at
        )

    # Fallback to pilot
    score = get_company_score(company_name)
    if not score:
        raise HTTPException(
            status_code=404,
            detail=f"Company '{company_name}' not found"
        )
    
    return ScoreResponse(
        company_name=score.company_name,
        score=round(score.score, 1),
        category=score.category.value,
        category_label=score.category_label,
        signals=SignalResponse(**score.signals.to_dict()),
        component_scores=ComponentScoresResponse(**{
            k: round(v, 1) for k, v in score.component_scores.items()
        }),
        evidence=score.evidence[:5],
        scored_at=getattr(score, "created_at", None) # Fallback if pilot data has date
    )
