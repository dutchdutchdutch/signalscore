"""Company repository - database operations for Company model."""

from typing import Optional
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from app.models import Company, CompanySource
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

    # Story 5-7: Source Management
    def get_source_by_url(self, company_id: int, url: str) -> Optional[CompanySource]:
        """Get existing source for company."""
        # Avoid circular import
        from app.models import CompanySource
        return (
            self.db.query(CompanySource)
            .filter(CompanySource.company_id == company_id, CompanySource.url == url)
            .first()
        )

    def add_source(
        self, 
        company_id: int, 
        url: str, 
        verification_status: str,
        submitted_by: Optional[str] = None
    ) -> CompanySource:
        """Add a new source to the company."""
        from app.models import CompanySource
        from app.models.enums import SourceType
        
        source = CompanySource(
            company_id=company_id,
            url=url,
            source_type=SourceType.OTHER, # Default to OTHER, discovery agent can refine
            verification_status=verification_status,
            submitted_by=submitted_by,
            is_active=True
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def count_recent_pending_sources(self, company_id: int, hours: int = 1) -> int:
        """Count pending sources submitted in the last N hours."""
        from app.models import CompanySource
        from app.models.enums import VerificationStatus
        from datetime import datetime, timedelta, timezone

        # Approximate 'created_at' using 'last_scraped_at' which defaults to now() on creation
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        
        return (
            self.db.query(CompanySource)
            .filter(
                CompanySource.company_id == company_id,
                CompanySource.verification_status == VerificationStatus.PENDING,
                # Note: last_scraped_at is timezone aware if DB is configured right, 
                # but careful with SQLite naive datetimes. 
                # Assuming standard UTC or naive-as-UTC storage.
                CompanySource.last_scraped_at >= cutoff 
            )
            .count()
        )
