from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Any, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl

from app.core.database import get_db
from app.models.company import Company
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/admin", tags=["admin"])


class RescoreRequest(BaseModel):
    """Request model for manual rescore endpoint."""
    company_name: str
    careers_url: HttpUrl  # L1 Fix: Validate URL format
    evidence_urls: Optional[List[str]] = None
    research_mode: bool = False


class RescoreResponse(BaseModel):
    """Response model for manual rescore endpoint."""
    status: str
    company_name: str
    score: float
    category: str
    sources_scraped: int
    sources_saved: int
    message: str


@router.get("/failures")
def get_failures(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Get list of companies with potential failures or low scores.
    Returns lightweight objects with discovery_trace.
    """
    # Fetch all companies, sorted by recency
    stmt = select(Company).order_by(Company.updated_at.desc()).limit(100)
    companies = db.execute(stmt).scalars().all()
    
    results = []
    for comp in companies:
        latest_score_val = 0.0
        scored_at = None
        
        if comp.scores:
            # Assumes relationship order_by is desc(created_at)
            latest_score = comp.scores[0]
            latest_score_val = latest_score.score
            scored_at = latest_score.created_at
        
        # Filter Logic (AC1): Score < 10 or simply showing all recent for diagnostics
        # We'll include if score < 15 (raising threshold slightly) OR if it has a trace
        if latest_score_val < 15.0 or comp.discovery_trace:
            # AC3: Failure Categorization
            probable_cause = "Unknown"
            trace = comp.discovery_trace or {}
            steps = trace.get("steps", [])
            steps_str = str(steps).lower() # Lazy search
            
            if "403" in steps_str or "429" in steps_str or "captcha" in steps_str:
                probable_cause = "Blocked"
            elif "found 0 potential sources" in steps_str or "found 0 subdomains" in steps_str:
                 # Refine ghost detection: if basically nothing was found
                 if "deep scraping 0" in steps_str:
                     probable_cause = "Ghost"
            elif latest_score_val < 5.0:
                 probable_cause = "Empty"

            results.append({
                "id": comp.id,
                "name": comp.name,
                "score": round(latest_score_val, 1),
                "updated_at": comp.updated_at,
                "scored_at": scored_at,
                "trace": comp.discovery_trace,
                "probable_cause": probable_cause
            })
            
    return results


@router.post("/rescore", response_model=RescoreResponse)
async def rescore_company(
    request: RescoreRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> RescoreResponse:
    """
    Story 4-6: Manually trigger a rescore for a company with optional evidence URLs.
    
    - **company_name**: Name of the company to rescore
    - **careers_url**: Main careers URL for the company
    - **evidence_urls**: Optional list of additional URLs to scrape for evidence
    - **research_mode**: If true, auto-discover sources via web search
    """
    service = ScoringService(db)
    
    try:
        result = await service.manual_rescore(
            company_name=request.company_name,
            careers_url=str(request.careers_url),
            evidence_urls=request.evidence_urls,
            research_mode=request.research_mode
        )
        
        return RescoreResponse(
            status="completed",
            company_name=result["company_name"],
            score=result["score"],
            category=result["category"],
            sources_scraped=result["sources_scraped"],
            sources_saved=result["sources_saved"],
            message=f"Successfully rescored {result['company_name']} with {result['sources_scraped']} sources."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rescore failed: {str(e)}")


# Story 4-8: Domain Alias Management

class DomainAliasRequest(BaseModel):
    """Request model for creating a domain alias."""
    company_id: int
    alias_domain: str


class DomainAliasResponse(BaseModel):
    """Response model for domain alias operations."""
    id: int
    company_id: int
    alias_domain: str
    created_at: datetime


@router.post("/domain-alias", response_model=DomainAliasResponse)
def create_domain_alias(
    request: DomainAliasRequest,
    db: Session = Depends(get_db)
) -> DomainAliasResponse:
    """
    Story 4-8: Register an alias domain for a company.
    
    - **company_id**: ID of the parent company
    - **alias_domain**: The alias domain to register (e.g., 'google.dev')
    """
    from app.models.company import Company, CompanyDomainAlias
    
    # Verify company exists
    company = db.execute(
        select(Company).where(Company.id == request.company_id)
    ).scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ID {request.company_id} not found")
    
    # Normalize domain (remove www., lowercase)
    normalized_domain = request.alias_domain.lower().replace("www.", "")
    
    # Check if alias already exists
    existing = db.execute(
        select(CompanyDomainAlias).where(CompanyDomainAlias.alias_domain == normalized_domain)
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=400, 
            detail=f"Alias '{normalized_domain}' already registered to company ID {existing.company_id}"
        )
    
    # Create the alias
    alias = CompanyDomainAlias(
        company_id=request.company_id,
        alias_domain=normalized_domain
    )
    db.add(alias)
    db.commit()
    db.refresh(alias)
    
    return DomainAliasResponse(
        id=alias.id,
        company_id=alias.company_id,
        alias_domain=alias.alias_domain,
        created_at=alias.created_at
    )


@router.get("/domain-alias/{company_id}", response_model=List[DomainAliasResponse])
def get_domain_aliases(
    company_id: int,
    db: Session = Depends(get_db)
) -> List[DomainAliasResponse]:
    """
    Story 4-8: Get all domain aliases for a company.
    
    - **company_id**: ID of the company to get aliases for
    """
    from app.models.company import Company, CompanyDomainAlias
    
    # Verify company exists
    company = db.execute(
        select(Company).where(Company.id == company_id)
    ).scalar_one_or_none()
    
    if not company:
        raise HTTPException(status_code=404, detail=f"Company with ID {company_id} not found")
    
    # Get all aliases
    aliases = db.execute(
        select(CompanyDomainAlias).where(CompanyDomainAlias.company_id == company_id)
    ).scalars().all()
    
    return [
        DomainAliasResponse(
            id=a.id,
            company_id=a.company_id,
            alias_domain=a.alias_domain,
            created_at=a.created_at
        )
        for a in aliases
    ]


