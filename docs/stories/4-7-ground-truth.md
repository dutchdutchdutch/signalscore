# Story 4-7: Ground Truth Benchmarking

## Status
- **Status:** done
- **Priority:** Low
- **Effort:** Small

## Story
**As an** Admin,
**I want** to upload "Ground Truth" datasets (reference companies with known-correct scores),
**So that** I can validate the system's scoring accuracy and regress against improvements.

## Context
To ensure our `ScoringService` is accurate, we need a benchmark. We will define a "Golden Set" of companies with manually verified scores. The system should be able to run against this set and report how close the algorithmic scores are to the human-verified truth.

## Acceptance Criteria

### AC1: Ground Truth Data Format
**Given** a JSON file `ground_truth.json`,
**When** the system reads it,
**Then** it parses a list of companies with expected scores and expected signals.
Example format:
```json
[
  {
    "domain": "stripe.com",
    "expected_score": 85,
    "tolerance": 0.5,
    "notes": "Agentic commerce, Engineering blog, github stripe/ai, Stripe MCP"
  }
]
```

### AC2: Benchmark Script
**Given** a ground truth file,
**When** I run `python execution/backend/scripts/run_benchmark.py --file data/ground_truth.json`,
**Then** the script:
1.  Loads the companies.
2.  Runs `ScoringService.manual_rescore` (or equivalent) for each.
3.  Compares calculated score vs expected score.

### AC3: Accuracy Report
**Given** the benchmark has run,
**When** it completes,
**Then** it outputs a summary report:
-   Total Accuracy (e.g. "85% within tolerance")
-   Mean Absolute Error (MAE)
-   List of "Misses" (companies where score deviated beyond tolerance).

## Tasks
- [x] **Backend**
    - [x] Define `GroundTruthItem` Pydantic model.
    - [x] Create `execution/backend/data/ground_truth_seed.json` with 3-5 top/bottom tier companies.
    - [x] Create `execution/backend/scripts/run_benchmark.py`.
    - [x] Implement scoring loop and comparison logic.
    - [x] Implement reporting output (CLI table).
- [x] **Verification**
    - [x] Run benchmark against seed data and verify output format.

## Dev Agent Record

### File List
- execution/backend/app/schemas/benchmark.py
- execution/backend/data/ground_truth_seed.json
- execution/backend/scripts/run_benchmark.py
- execution/backend/app/services/scoring_service.py

### Change Log
- **[NEW] `GroundTruthItem` Model**: Defined Pydantic model for benchmark items.
- **[NEW] Seed Data**: Created `ground_truth_seed.json` with initial validation set (Stripe, Dropbox, Example).
- **[NEW] Benchmark Script**: Implemented `run_benchmark.py` to executing scoring and report accuracy/MAE.
- **[FIX] Scoring Stability**: Updated `scoring_service.py` to handle duplicate DB records gracefully and fixed `DiscoveryService` calls during benchmark execution.
