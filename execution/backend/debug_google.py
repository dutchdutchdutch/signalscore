import sys
from app.core.database import SessionLocal
from app.models.company import Company
from app.schemas.scores import ScoreResponse, SignalResponse, ComponentScoresResponse
from sqlalchemy import select

def check():
    db = SessionLocal()
    company = db.execute(select(Company).where(Company.name == "Google")).scalar_one_or_none()
    
    if not company:
        print("Company 'Google' not found in DB")
        return

    score = company.scores[0]
    print(f"Found Score: {score.score}")
    print(f"Signals type: {type(score.signals)}")
    print(f"Signals keys: {score.signals.keys()}")
    
    try:
        # Simulate what the API does
        resp = ScoreResponse(
            company_name=company.name,
            careers_url=company.careers_url,
            score=round(score.score, 1),
            category=score.category.value,
            category_label=score.category.value.replace("_", "-").title(),
            signals=SignalResponse(**score.signals),
            component_scores=ComponentScoresResponse(**score.component_scores),
            evidence=score.evidence,
            scored_at=score.created_at
        )
        print("Validation Successful!")
    except Exception as e:
        print(f"Validation FAILED: {e}")
        # Print details
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check()
