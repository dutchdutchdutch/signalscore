"""Companies API router - search and CRUD endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import CompanyRead, CompanyCreate, CompanyList, CompanySourceSubmission
from app.services.company_repository import CompanyRepository
from app.services.scoring_service import ScoringService
from app.models.enums import VerificationStatus
from fastapi import BackgroundTasks
import tldextract

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("/search", response_model=list[CompanyRead])
def search_companies(
    q: str = Query(..., min_length=1, description="Search query (company name or URL)"),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db: Session = Depends(get_db),
) -> list[CompanyRead]:
    """
    Search for companies by name or URL.
    
    Returns matching companies with camelCase field names.
    Returns empty list if no matches found.
    """
    repo = CompanyRepository(db)
    companies, _total = repo.search(q, limit=limit, offset=offset)
    
    return [CompanyRead.model_validate(c) for c in companies]


@router.get("/search/detailed", response_model=CompanyList)
def search_companies_detailed(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> CompanyList:
    """
    Search with pagination metadata.
    
    Returns companies plus total count for pagination.
    """
    repo = CompanyRepository(db)
    companies, total = repo.search(q, limit=limit, offset=offset)
    
    return CompanyList(
        items=[CompanyRead.model_validate(c) for c in companies],
        total=total,
    )


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(
    company_id: int,
    db: Session = Depends(get_db),
) -> CompanyRead:
    """Get a company by ID."""
    repo = CompanyRepository(db)
    company = repo.get_by_id(company_id)
    
    if not company:
        raise HTTPException(
            status_code=404,
            detail=f"Company with ID {company_id} not found",
        )
    
    return CompanyRead.model_validate(company)


@router.post("", response_model=CompanyRead, status_code=201)
def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
) -> CompanyRead:
    """Create a new company."""
    repo = CompanyRepository(db)
    
    # Check if company with same name already exists
    existing = repo.get_by_name(company_data.name)
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"Company '{company_data.name}' already exists",
        )
    
    company = repo.create(company_data)
    return CompanyRead.model_validate(company)


@router.get("", response_model=list[CompanyRead])
def list_companies(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[CompanyRead]:
    """List all companies with pagination."""
    repo = CompanyRepository(db)
    companies = repo.get_all(limit=limit, offset=offset)
    
    return [CompanyRead.model_validate(c) for c in companies]


@router.post("/{company_id}/sources", status_code=202)
async def submit_sources(
    company_id: int,
    submission: CompanySourceSubmission,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Submit URLs for a company.
    
    - Auto-verifies if domain matches company.
    - Sets to PENDING if domain differs (requires admin review).
    - Triggers rescore if valid sources added.
    """
    repo = CompanyRepository(db)
    company = repo.get_by_id(company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    # Rate Limit Check
    pending_count = repo.count_recent_pending_sources(company_id)
    if pending_count >= 3:
         raise HTTPException(
             status_code=429, 
             detail="Too many pending submissions. Limit is 3 per hour."
         )

    added_verified = 0
    added_pending = 0
    
    # helper for domain check
    def get_root_domain(url: str) -> str:
        ext = tldextract.extract(url)
        return f"{ext.domain}.{ext.suffix}"

    company_root = company.domain or get_root_domain(company.url or "")

    for url_obj in submission.urls:
        url = str(url_obj)
        
        # Check duplicate
        if repo.get_source_by_url(company_id, url):
            continue
            
        # Verify Domain
        src_root = get_root_domain(url)
        # Using strict equality on root domain (google.com == google.com)
        if src_root == company_root:
            status = VerificationStatus.VERIFIED
            added_verified += 1
        else:
            status = VerificationStatus.PENDING
            added_pending += 1
            
        repo.add_source(company_id, url, status.value, submitted_by="user")

    # Trigger Rescore if new verified data
    if added_verified > 0 and company.url:
        service = ScoringService(db)
        # We call score_company directly to force re-evaluation with new sources
        background_tasks.add_task(service.score_company, company.url)

    return {
        "message": "Sources submitted",
        "verified_count": added_verified,
        "pending_count": added_pending,
        "status": "processing" if added_verified > 0 else "queued"
    }
