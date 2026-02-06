"""Company repository - database operations for Company model."""

from typing import Optional
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models import Company
from app.schemas import CompanyCreate, CompanyUpdate


class CompanyRepository:
    """Repository pattern for Company database operations."""

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, company_id: int) -> Optional[Company]:
        """Get a company by ID."""
        return self.db.query(Company).filter(Company.id == company_id).first()

    def get_by_name(self, name: str) -> Optional[Company]:
        """Get a company by exact name match."""
        return self.db.query(Company).filter(Company.name == name).first()

    def get_by_url(self, url: str) -> Optional[Company]:
        """Get a company by URL."""
        return self.db.query(Company).filter(Company.url == url).first()

    def search(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Company], int]:
        """
        Search companies by name or URL.
        
        Args:
            query: Search term (matched against name and URL)
            limit: Maximum results to return
            offset: Pagination offset
            
        Returns:
            Tuple of (matching companies, total count)
        """
        # Normalize query
        search_term = f"%{query.strip().lower()}%"
        
        # Build base query with case-insensitive search
        base_query = self.db.query(Company).filter(
            or_(
                func.lower(Company.name).like(search_term),
                func.lower(Company.url).like(search_term),
            )
        )
        
        # Get total count
        total = base_query.count()
        
        # Get paginated results
        companies = (
            base_query
            .order_by(Company.name)
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        return companies, total

    def get_all(self, limit: int = 100, offset: int = 0) -> list[Company]:
        """Get all companies with pagination."""
        return (
            self.db.query(Company)
            .order_by(Company.name)
            .offset(offset)
            .limit(limit)
            .all()
        )

    def create(self, company_data: CompanyCreate) -> Company:
        """Create a new company."""
        company = Company(
            name=company_data.name,
            url=company_data.url,
        )
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def update(self, company_id: int, company_data: CompanyUpdate) -> Optional[Company]:
        """Update an existing company."""
        company = self.get_by_id(company_id)
        if not company:
            return None
        
        update_data = company_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(company, field, value)
        
        self.db.commit()
        self.db.refresh(company)
        return company

    def delete(self, company_id: int) -> bool:
        """Delete a company by ID."""
        company = self.get_by_id(company_id)
        if not company:
            return False
        
        self.db.delete(company)
        self.db.commit()
        return True

    def count(self) -> int:
        """Get total company count."""
        return self.db.query(Company).count()
