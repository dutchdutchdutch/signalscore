#!/usr/bin/env python3
"""
Story 4-7: Ground Truth Benchmark Script.
Runs the scoring service against a set of known companies and compares results.
"""
import sys
import os
import json
import asyncio
import textwrap
from typing import List
from pathlib import Path

# Add project root to path so we can import app modules
# Assumes script is run from project root or execution/backend/scripts
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "execution" / "backend"))

from app.schemas.benchmark import GroundTruthItem
from app.services.scoring_service import ScoringService
from app.core.database import SessionLocal
from sqlalchemy.orm import Session

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

async def run_benchmark(file_path: str):
    """
    AC2: Benchmarking Logic
    1. Loads companies from ground_truth.json
    2. Runs ScoringService.manual_rescore for each
    3. Compares calculated vs expected
    """
    
    # Validation: File existence
    path = Path(file_path)
    if not path.exists():
        # Fallback to local data dir if just filename provided
        path = PROJECT_ROOT / "execution" / "backend" / "data" / file_path
        if not path.exists():
            print(f"{RED}Error: File {file_path} not found.{RESET}")
            sys.exit(1)
            
    print(f"Loading ground truth from: {path}")
    
    # AC1: Parse JSON
    try:
        with open(path, "r") as f:
            data = json.load(f)
            items = [GroundTruthItem(**item) for item in data]
    except Exception as e:
        print(f"{RED}Error parsing ground truth file: {e}{RESET}")
        sys.exit(1)
        
    print(f"Loaded {len(items)} companies to benchmark.\n")
    
    db = SessionLocal()
    service = ScoringService(db)
    
    results = []
    total_accuracy = 0
    total_mae = 0
    misses = []
    
    print(f"{'Company':<20} | {'Exp':<5} | {'Act':<5} | {'Diff':<5} | {'Result'}")
    print("-" * 65)
    
    # Scoring Loop
    for item in items:
        try:
            # We use manual_rescore in research mode to ensure fresh data
            # Map domain to url for initial connection
            careers_url = f"https://{item.domain}/careers" 
            
            # Run scoring
            # Note: manual_rescore returns a dict
            score_result = await service.manual_rescore(
                company_name=item.domain, # Use domain as name for matching
                careers_url=careers_url,
                research_mode=True # Force new discovery
            )
            
            actual_score = score_result["score"]
            diff = actual_score - item.expected_score
            abs_diff = abs(diff)
            
            is_pass = abs_diff <= item.tolerance
            
            status_color = GREEN if is_pass else RED
            status_icon = "✅" if is_pass else "❌"
            
            print(f"{item.domain:<20} | {item.expected_score:<5} | {actual_score:<5} | {diff:<+5.1f} | {status_icon}")
            
            results.append({
                "item": item,
                "actual": actual_score,
                "diff": diff,
                "pass": is_pass
            })
            
            total_mae += abs_diff
            if is_pass:
                total_accuracy += 1
            else:
                misses.append(item)
                
        except Exception as e:
            print(f"{RED}Failed to score {item.domain}: {e}{RESET}")
            
    # AC3: Accuracy Report
    count = len(items)
    accuracy_pct = (total_accuracy / count) * 100 if count > 0 else 0
    mae = total_mae / count if count > 0 else 0
    
    print("\n" + "="*30)
    print("BENCHMARK SUMMARY")
    print("="*30)
    print(f"Total Companies: {count}")
    print(f"Accuracy (within tolerance): {accuracy_pct:.1f}%")
    print(f"Mean Absolute Error (MAE): {mae:.1f}")
    
    if misses:
        print("\nMisses (Out of Tolerance):")
        for miss in misses:
            print(f"- {miss.domain}: Expected {miss.expected_score} +/- {miss.tolerance}, "
                  f"Actual {next(r['actual'] for r in results if r['item'] == miss)}")
            if miss.notes:
                print(f"  Notes: {miss.notes}")
                
    db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_benchmark.py <ground_truth_file.json>")
        print("Example: python run_benchmark.py ground_truth_seed.json")
        sys.exit(1)
        
    file_arg = sys.argv[1]
    asyncio.run(run_benchmark(file_arg))
