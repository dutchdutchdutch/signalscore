# Story 4.5: Scraper Failures & Diagnostics

## Status
- **Status:** done
- **Priority:** Medium
- **Effort:** Small

## Story
**As an** Admin Operator,
**I want** to view a dashboard of companies where scraping failed or resulted in a low score,
**So that** I can diagnose if the issue is a technical block (429/403), a missing source, or simply a lack of public signals.

## Context
With the automated resilience from Stories 4.3 and 4.4, systemic failures are rare. However, some companies (e.g., Fidelity, Netflix) still receive low scores (0.0 - 6.0). We need visibility into *why* these happen without checking server logs. This story focuses on **Monitoring & Diagnostics** only; manual retry actions are deferred to Story 4.6.

## Acceptance Criteria
1.  **AC1: Failure Dashboard UI**
    - A new Admin page (`/admin/failures`) listing high-risk companies.
    - Criteria for "risk": Score < 10.0 OR `scrape_status` != "success".
    - Columns: Company Name, Current Score, Last Scraped At, Primary Error (if any).

2.  **AC2: Diagnostic Trace Display**
    - Clicking a company in the list opens a detail view showing the `DiscoveryService` decision trace.
    - Must show:
        - Subdomains found (or 0 found).
        - Search queries attempted and their results (e.g., "site:github.com ... -> 0 results").
        - HTTP Status codes for key sources (e.g., "Careers Page: 403 Forbidden").

3.  **AC3: Failure Categorization**
    - The system should tag failures with a "Probable Cause":
        - **"Blocked"**: 403/429 errors detected.
        - **"Ghost"**: 0 sources found after all attempts.
        - **"Empty"**: Sources found but 0 signals extracted (content parsing issue).

## Technical Notes
- **Backend:** Create `GET /api/admin/failures` endpoint.
- **Frontend:** New `AdminLayout` and `FailureList` component.
- **Data:** Ensure `ScoringService` saves the "Discovery Trace" (log of steps) to the `Score` or `Company` model (JSON column or similar) so it can be retrieved.

## Tasks
- [x] **Backend**
    - [x] Update `ScoringService` to persist discovery/scraping logs (Decision Trace).
    - [x] Create `GET /api/admin/failures` endpoint.
- [x] **Frontend**
    - [x] Create `/admin/failures` page.
    - [x] Implement `FailureList` table.
    - [x] Implement `DiagnosticLog` viewer (collapsible JSON or list).
- [x] **Verification**
    - [x] Verify Fidelity/Netflix logs appear in the dashboard.

## Dev Agent Record

### File List
- execution/backend/app/models/company.py
- execution/backend/alembic/versions/604b561c99c9_add_discovery_trace_to_company.py
- execution/backend/app/services/scoring_service.py
- execution/backend/app/api/v1/admin.py
- execution/backend/app/api/v1/router.py
- execution/frontend/src/app/admin/layout.tsx
- execution/frontend/src/app/admin/failures/page.tsx
- execution/frontend/src/components/admin/FailureList.tsx
- execution/frontend/src/components/admin/DiagnosticLog.tsx
- execution/backend/tests/test_scoring_trace.py
- execution/backend/tests/test_admin_api.py

### Change Log
- **Review Follow-ups (AI):**
    - [x] [High] Implemented AC3 (Failure Categorization) logic in backend and frontend.
    - [x] [Medium] Added `test_admin_api.py` to verify failure logic.
    - Note: User waived authentication requirement for admin API.
