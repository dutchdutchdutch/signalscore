# Story 4.6: Manual Rescore & Evidence Injection

## Status
- **Status:** done
- **Priority:** Medium
- **Effort:** Small

## Story
**As an** Admin Operator,
**I want** to manually trigger a rescore for a specific company with optional evidence URLs,
**So that** I can correct scores for companies that were blocked, had stale data, or need updated analysis from new sources.

## Context
Story 4.5 introduced a diagnostics dashboard showing companies with failed scrapes or low scores. This story provides the **action** capability to fix those cases. The `rescore_company.py` script already exists but is CLI-only. We need a UI-accessible version with optional evidence injection.

### Related Work
- **Story 4.5:** Exposes the list of companies needing attention.
- **`scripts/rescore_company.py`:** Contains the core logic for rescoring with evidence.
- **`DiscoveryService`:** Provides `--research` mode for automatic source discovery.

## Acceptance Criteria

### AC1: Manual Rescore API Endpoint
**Given** an admin viewing a company in the failures dashboard,
**When** they trigger a rescore via API (`POST /api/admin/rescore`),
**Then** the system re-runs the full scoring pipeline for that company and updates the database.

**Request Body:**
```json
{
  "company_name": "Google",
  "careers_url": "https://careers.google.com",
  "evidence_urls": ["https://blog.google/ai", "https://github.com/google"],  // Optional
  "research_mode": true  // Optional: auto-discover sources
}
```

### AC2: Evidence URL Injection
**Given** a rescore request with `evidence_urls` provided,
**When** the scoring runs,
**Then** those URLs are scraped and included in signal extraction, with `source_attribution` reflecting them.

### AC3: Rescore Button in UI
**Given** the failures dashboard (`/admin/failures`),
**When** an admin clicks "Rescore" on a company row,
**Then** a modal opens allowing them to:
- Confirm the default careers URL or edit it.
- Optionally add evidence URLs.
- Toggle "Research Mode" (auto-discover).
- Submit the rescore request.

### AC4: Progress Feedback
**Given** a rescore is triggered,
**When** the process is running,
**Then** the UI shows "Rescoring..." status and refreshes the score upon completion.

## Technical Notes
- **Backend:** Refactor `rescore_company.py` logic into a reusable service function. Create `POST /api/admin/rescore` endpoint.
- **Frontend:** Add `RescoreModal` component with form fields. Integrate with `FailureList` row.
- **Async:** Rescore should run as a background task (like `score_company`).

## Tasks
- [x] **Backend**
    - [x] Extract `rescore_company.py` logic into `ScoringService.manual_rescore()` method.
    - [x] Create `POST /api/admin/rescore` endpoint in `admin.py`.
    - [x] Add input validation (company_name required, URL format check).
- [x] **Frontend**
    - [x] Create `RescoreModal` component with form fields.
    - [x] Add "Rescore" button to `FailureList` rows.
    - [x] Implement loading state and success/error toast.
- [x] **Verification**
    - [x] Test rescore API endpoint with curl.
    - [x] Verify sources are scraped and saved.

## Dev Agent Record

### File List
- `execution/backend/app/services/scoring_service.py` (added `manual_rescore()` method with `detect_source_type()`)
- `execution/backend/app/api/v1/admin.py` (added `POST /rescore` endpoint + Pydantic schemas)
- `execution/backend/scripts/rescore_company.py` (bug fix: source type detection for non_eng_ai scoring)
- `execution/frontend/src/components/admin/RescoreModal.tsx` (new)
- `execution/frontend/src/components/admin/FailureList.tsx` (integrated Rescore button + modal)
- `execution/frontend/src/components/features/CompanySearch.tsx` (bug fix: domain extraction for slug)
- `execution/frontend/src/components/ui/CompanyCard.tsx` (bug fix: use domain for slug, not URL)
- `execution/frontend/src/components/ui/__tests__/CompanyCard.test.tsx` (updated tests for domain field)
- `execution/frontend/src/lib/api-client/schema.d.ts` (added `domain` field to CompanyRead)
- `docs/stories/sprint-status.yaml` (updated story status)

### Change Log
- **2026-02-05:** Implementation complete.
    - [x] Backend: `ScoringService.manual_rescore()` with evidence injection and research mode.
    - [x] Backend: `POST /api/v1/admin/rescore` endpoint with `RescoreRequest`/`RescoreResponse` schemas.
    - [x] Frontend: `RescoreModal` component with form fields.
    - [x] Frontend: Integrated Rescore button into `FailureList`.
    - [x] Verification: API endpoint tested via curl, returned valid response.
- **2026-02-05:** Bug fixes during testing.
    - [x] Fixed subdomain link issue (`CompanyCard.tsx`, `CompanySearch.tsx`).
    - [x] Fixed `non_eng_ai` scoring for PM job postings (`rescore_company.py`, `scoring_service.py`).
- **2026-02-05:** Code review fixes.
    - [x] L1: Added URL validation to `careers_url` field.
    - [x] L2: Modal state resets on close.
    - [x] M2: Changed to relative API URL for staging/production.
    - [x] M3: Added safe JSON error parsing.
