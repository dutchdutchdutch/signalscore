import sys
from app.core.database import SessionLocal
from app.models.company import Company
from sqlalchemy import select

def delete_company(name="Google"):
    db = SessionLocal()
    # Check by name
    company = db.execute(select(Company).where(Company.name == name)).scalar_one_or_none()
    
    if not company:
        # Check by domain if name failed
        company = db.execute(select(Company).where(Company.domain == "google.com")).scalar_one_or_none()
    
    if company:
        print(f"Deleting Company: {company.name} (ID: {company.id})")
        # Cascade delete should handle scores/sources if configured, 
        # otherwise we might need manual delete.
        # Assuming cascade or basic delete is fine for MVP.
        db.delete(company)
        db.commit()
        print("Deletion confirmed.")
    else:
        print(f"Company '{name}' not found.")

if __name__ == "__main__":
    delete_company()
