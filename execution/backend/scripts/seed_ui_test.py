
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.company import Company, Score
from app.models.enums import AIReadinessCategory

def seed_data():
    db: Session = SessionLocal()
    
    # Check if FakeLeading exists
    existing = db.query(Company).filter(Company.name == "FakeLeading").first()
    if existing:
        print("FakeLeading already exists. Skipping.")
        db.close()
        return

    print("Seeding FakeLeading...")
    company = Company(name="FakeLeading", domain="fakeleading.com", careers_url="https://fakeleading.com")
    db.add(company)
    db.commit()
    
    score = Score(
        company_id=company.id,
        score=90.0,
        category=AIReadinessCategory.LEADING,
        signals={
            "ai_keywords": 90,
            "agentic_signals": 0,
            "tool_stack": [],
            "non_eng_ai_roles": 0,
            "has_ai_platform_team": False,
            "jobs_analyzed": 5
        },
        component_scores={
            "ai_keywords": 90.0,
            "agentic_signals": 0.0,
            "tool_stack": 0.0,
            "non_eng_ai": 0.0,
            "ai_platform_team": 0.0
        },
        evidence=["Seeded High Score Evidence"]
    )
    db.add(score)
    db.commit()
    db.close()
    print("Seeding complete.")

if __name__ == "__main__":
    seed_data()
