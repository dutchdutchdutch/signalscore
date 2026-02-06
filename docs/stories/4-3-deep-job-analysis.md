# Story 4.3: Deep Job Analysis & Resilience

## Status
- **Status:** review
- **Priority:** High
- **Effort:** Medium

## Story
**As a** Score Consumer,
**I want** the system to prioritize and deeply analyze Job Descriptions (JDs) even if external search fails,
**So that** companies like Google and Netflix receive accurate AI scores based on their hiring intent, which is the most reliable signal of internal activity.

## Context
Initial evaluation of Story 4.2 showed that known AI leaders (Google, Netflix) received `0.0` scores. This was due to:
1.  **Search Rate Limits:** `DiscoveryService` failed (429) to find satellite sources (GitHub, Blogs).
2.  **Fragile Fallback:** When search failed, the system relied solely on the Homepage, which (correctly) was penalized for "Marketing Only" or had low weight.
3.  **JD Under-utilization:** The user identified that "Job descriptions are the most telling." We need to treat them as a **Primary Verified Source**, not just another text segment.

## Acceptance Criteria
1.  **AC1: ATS & Career Page Detection**
    - System must explicitly scan for common ATS domains (greenhouse.io, lever.co, myworkday, ashby) within the `careers_url` or Homepage.
    - These sources should be treated as "High Confidence" (similar weight to GitHub).

2.  **AC2: Resilience to Rate Limits**
    - If Google Search fails (429), the system must trigger an "Emergency Crawl" mode: 
    - deeper recursive link following on the provided domain (depth=2 or 3) specifically looking for `/jobs`, `/careers`.

3.  **AC3: JD Parsing & Weighting**
    - Text identified as a Job Description should be analyzed for:
        - **"Required Skills":** High weight (it's verified need).
        - **"About the team":** Context signal.
    - Presence of "PyTorch" in a JD should count as **Verified Tool Stack** (Weight 1.5 - 2.0), resolving "Marketing Only" conflicts.

4.  **AC4: Evaluation Threshold**
    - Re-running the benchmark for Google/Netflix (without search) should yield a score > 40.0 purely based on crawling their career pages.

## Technical Notes
- **Services:** `DiscoveryService` (add ATS heuristics), `ScraperOrchestrator` (add Deep Crawl mode).
- **Weights:** Update `calculator.py` to boost `job_posting` weight if it matches specific patterns (e.g., "Requirements", "Qualifications").

## Tasks
- [x] **Discovery Improvements**
    - [x] Implement `ATSDetector` to find Greenhouse/Lever links.
    - [x] Implement "Emergency Crawl" fallback when Search fails.
- [x] **Scoring Logic**
    - [x] Boost `job_posting` weight to 1.5 or 2.0 (Verified Source).
    - [x] Refine `_extract_signals` to parse "Required Skills" sections if possible.
- [x] **Verification**
    - [x] Verify Google/Netflix score recovery.
    - [x] Run `evaluate_improvements.py` again.

## Dev Agent Record

### Implementation Plan
1. Created `ATSDetector` class for ATS platform detection (AC1)
2. Added 429 rate-limit detection in `DiscoveryService._perform_search()` (AC2)
3. Implemented `_emergency_crawl()` method in `ScoringService` (AC2)
4. Boosted `job_posting` weight from 1.0 to 2.0 in both weight maps (AC3)
5. Added `job_posting` to `eng_sources` list to resolve marketing_only conflicts (AC3)
6. Enhanced `_find_job_links()` to detect ATS embeds via iframes and anchor tags (AC1)
7. Fixed missing `CATEGORY_THRESHOLDS` import in `calculator.py` (bug fix)
8. Added "ashby.io" to Selenium scraper's `JS_HEAVY_PATTERNS` (AC1)

### Debug Log
- Fixed missing `Dict` and `re` imports in `scoring_service.py`
- Pre-existing test failures (10) in API/DB tests unrelated to Story 4-3

### Completion Notes
- All 4 ACs implemented with tests
- 30 core tests pass (0 regressions)
- JD weight boost from 1.0 → 2.0 treats job descriptions as verified sources
- Emergency crawl triggers when `discovery.search_failed` is True

## File List
- `execution/backend/app/services/scrapers/ats_detector.py` (new)
- `execution/backend/app/services/scrapers/__init__.py` (modified)
- `execution/backend/app/services/scrapers/selenium_scraper.py` (modified)
- `execution/backend/app/services/discovery.py` (modified)
- `execution/backend/app/services/scoring_service.py` (modified)
- `execution/backend/app/services/scoring/calculator.py` (modified)
- `execution/backend/tests/test_ats_detector.py` (new)
- `execution/backend/tests/test_emergency_crawl.py` (new)
- `execution/backend/tests/test_jd_weighting.py` (new)

## Change Log
- Story 4.3: Deep Job Analysis & Resilience implementation (2026-02-05)
