
import asyncio
import sys
import os

# Set up path so we can import 'app'
# We are likely running from project root, so we need to add 'execution/backend'
sys.path.append(os.path.join(os.getcwd(), 'execution/backend'))

from app.core.database import SessionLocal
from app.models.company import Company, Score
from app.services.scoring_service import ScoringService
from sqlalchemy import select, desc
from unittest.mock import MagicMock
from app.services.scoring.model import get_category_label

# Simple table formatter
def print_table(rows):
    if not rows:
        print("No data.")
        return
    
    # Calculate widths
    widths = [max(len(str(val)) for val in col) for col in zip(*rows)]
    
    # Print header
    header = " | ".join(f"{str(val):<{width}}" for val, width in zip(rows[0], widths))
    print(header)
    print("-" * len(header))
    
    # Print rows
    for row in rows[1:]:
        print(" | ".join(f"{str(val):<{width}}" for val, width in zip(row, widths)))

async def main():
    print("Initializing Database Session...")
    db = SessionLocal()
    service = ScoringService(db)
    
    # 1. Fetch Companies and Benchmark Scores
    print("Fetching companies...")
    companies = db.query(Company).all()
    
    benchmarks = {}
    
    for company in companies:
        # Get latest score for benchmark
        # We assume scores are ordered or we sort them
        stmt = select(Score).where(Score.company_id == company.id).order_by(desc(Score.created_at))
        latest_score = db.execute(stmt).scalars().first()
        
        if latest_score:
            benchmarks[company.id] = {
                "score": latest_score.score,
                "created_at": latest_score.created_at
            }
        else:
            benchmarks[company.id] = {"score": "N/A", "created_at": None}

    print(f"Found {len(companies)} companies. Starting re-scoring...")
    
    # 2. Rerun Scores
    results = [["Company", "Benchmark Score", "New Score", "Difference", "Categories (Old -> New)"]]
    
    for company in companies:
        print(f"Re-scoring {company.name} ({company.careers_url})...")
        try:
            # We call the internal service method directly
            # Note: evaluate_improvements implies we want to see the effect of code changes on SAME data 
            # OR new data. Usage of 'score_company' will trigger scraping.
            # This might be slow.
            if not company.careers_url:
                print(f"Skipping {company.name} - No URL")
                continue
                
            await service.score_company(company.careers_url)
            

            
            # 3. Fetch New Score
            stmt = select(Score).where(Score.company_id == company.id).order_by(desc(Score.created_at))
            new_latest_score = db.execute(stmt).scalars().first()
            
            # Benchmark data
            benchmark_data = benchmarks.get(company.id)
            old_score = benchmark_data["score"]
            
            new_val = new_latest_score.score
            diff = "N/A"
            
            if old_score != "N/A":
                diff = round(new_val - float(old_score), 1)
                if diff > 0: diff = f"+{diff}"
            
            results.append([
                company.name, 
                old_score, 
                new_val, 
                diff,
                f"{get_category_label(new_latest_score.category)}"
            ])
            
        except Exception as e:
            print(f"Failed to rescore {company.name}: {e}")
            results.append([company.name, benchmarks[company.id]["score"], "ERROR", "ERROR", str(e)])

    print("\n\n=== IMPROVEMENT EVALUATION ===\n")
    print_table(results)

if __name__ == "__main__":
    asyncio.run(main())
