
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models.company import Company, Score
from app.core.database import Base

# Assuming default DB path
from app.core.database import SessionLocal

def check_company(name_query):
    db = SessionLocal()
    print(f"--- Checking for '{name_query}' ---")
    
    stmt = select(Company).where(
        (Company.name.ilike(f"%{name_query}%")) | 
        (Company.domain.ilike(f"%{name_query}%")) |
        (Company.careers_url.ilike(f"%{name_query}%"))
    )
    companies = db.execute(stmt).scalars().all()
    
    print(f"Found {len(companies)} companies matching '{name_query}'.")
    
    for c in companies:
        print(f"ID: {c.id}")
        print(f"Name: {c.name}")
        print(f"Domain: {c.domain}")
        print(f"Careers URL: {c.careers_url}")
        print(f"Created At: {c.created_at}")
        
        # Check scores
        if c.scores:
            print(f"  Scores ({len(c.scores)}):")
            for s in c.scores:
                print(f"    - Score: {s.score}, Category: {s.category}, Date: {s.created_at}")
        else:
            print("  No scores found.")
        print("-" * 20)

    db.close()

if __name__ == "__main__":
    check_company("nordstrom")
    check_company("target")
