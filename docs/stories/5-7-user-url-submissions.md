# Story 5-7: User URL Submissions

## Status
- **Status:** done
- **Priority:** Medium
- **Effort:** Medium

## Story
**As a** User (Company Owner or Employee),
**I want** to submit specific URLs for my company to be indexed,
**So that** the AI Readiness Score accurately reflects my organization's true digital footprint and isn't limited by crawler discovery gaps.

## Context
SignalScore relies on autonomous discovery, but sometimes crawlers miss specific subdomains, engineering blogs, or isolated careers pages. Users often want to "correct" the score by pointing the system to specific evidence. We want to allow this, but with safeguards against manipulation (e.g., submitting a competitor's high-scoring blog).

## Acceptance Criteria

### AC1: Submission Interface
**Given** a user is viewing a Company Scorecard (Result Page),
**Then** there should be a "Disagree with this score?" or "Improve this Score" section below the details.
**And** it should provide a form with spaces for up to **three (3)** specific URLs.
**And** the fields should be separate (no comma-separated lists) to reduce error.

### AC2: Auto-Verification Logic
**Given** a submitted URL,
**When** the user clicks "Submit",
**Then** the system should compare the submitted URL's root domain against the Company's canonical domain.
- **If Domain Matches**: Auto-verify the source, save it to the database, and trigger an immediate re-scoring (background job).
- **If Domain Differs**: Save the source as `verification_status="pending"` and inform the user: "External domain URLs must be verified by an administrator before processing."

### AC3: Backend Persistence
**Given** the submission,
**Then** valid URLs should be stored in the `company_sources` table.
**And** the table must support a verification status (`verified`, `pending`, `rejected`).
**And** existing scraping logic must be updated to ONLY use `verified` sources during scoring.

### AC4: Feedback Loop
**Given** an auto-verified submission,
**Then** the UI should show a "Processing..." state and reload the score once complete (or show a toast "Score update queue started").

## Technical Notes
- **Database**: Add `verification_status` (Enum) and `submitted_by` (optional, maybe IP or 'user') columns to `CompanySource`.
- **API**: Create `POST /api/v1/companies/{id}/sources` endpoint.
- **Validation**: Strict URL validation is required.
- **Security**: Rate limit submissions to prevent abuse. **Constraint**: Max 3 pending URLs per hour per company (DB-based check).

## Tasks
- [ ] Database Migration: Add `verification_status` to `CompanySource`.
- [ ] Backend: Update DB Model and Schema.
- [ ] Backend: Implement `POST /companies/{id}/sources` with domain check logic.
- [ ] Backend: Update Scoring Service to filter unverified sources.
- [ ] Frontend: Create `UrlSubmissionForm` component.
- [ ] Frontend: Integrate form into `CompanyDetails` page.
- [ ] Integration Test: Verify auto-accept vs. pending logic.

## File List
- `execution/backend/app/models/company.py`
- `execution/backend/app/schemas/source.py` (New)
- `execution/frontend/src/components/features/UrlSubmissionForm.tsx` (New)
- `execution/frontend/src/app/signal/[slug]/page.tsx`
