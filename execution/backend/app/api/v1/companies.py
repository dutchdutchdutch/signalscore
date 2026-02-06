"""Companies API router - search and CRUD endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas import CompanyRead, CompanyCreate, CompanyList
from app.services.company_repository import CompanyRepository

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
