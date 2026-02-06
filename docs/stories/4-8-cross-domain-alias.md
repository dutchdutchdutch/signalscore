# Story 4-8: Cross-Domain Alias Support

## Status
- **Status:** done
- **Priority:** Medium
- **Effort:** Small

## Story
**As an** Admin Operator,
**I want** to register alias domains for a company (e.g., `google.dev` → `Google`),
**So that** URLs from related but differently-named domains are correctly attributed to the parent company's score.

## Context
Large companies often own multiple TLDs for different products:
- Google: `google.com`, `google.dev`, `googleapis.com`, `withgoogle.com`
- Microsoft: `microsoft.com`, `azure.com`, `github.com`
- Amazon: `amazon.com`, `aws.com`, `aboutamazon.com`

Currently, each TLD is treated as a separate company. This story adds explicit alias mapping so evidence from related domains contributes to the parent company.

## Acceptance Criteria

### AC1: Domain Alias Model
**Given** the database schema,
**When** a `CompanyDomainAlias` table is created,
**Then** it contains `company_id`, `alias_domain`, and `created_at` columns.

### AC2: Alias Lookup in Domain Matching
**Given** a URL with a registered alias domain (e.g., `ai.google.dev`),
**When** the system resolves the company,
**Then** it matches the alias to the parent company (`Google`) instead of creating a new record.

### AC3: Admin API for Alias Management
**Given** an admin wants to register an alias,
**When** they call `POST /api/admin/domain-alias` with `company_id` and `alias_domain`,
**Then** the alias is saved and immediately active for lookups.

### AC4: Alias List in Company Details
**Given** a company with registered aliases,
**When** viewing company details (API or UI),
**Then** the list of alias domains is included in the response.

## Technical Notes
- **Model:** New `CompanyDomainAlias` table with FK to `companies`.
- **Lookup:** Modify `_get_or_create_company()` to check aliases before creating new company.
- **Migration:** Alembic migration for new table.

## Tasks
- [x] **Backend**
    - [x] Create `CompanyDomainAlias` model.
    - [x] Create Alembic migration.
    - [x] Update `_get_or_create_company()` to check alias table.
    - [x] Create `POST /api/admin/domain-alias` endpoint.
    - [x] Create `GET /api/admin/domain-alias/{company_id}` endpoint.
- [ ] **Frontend** (Optional)
    - [ ] Add alias management to admin UI.
- [x] **Verification**
    - [x] Test alias lookup with `google.dev` → `Google`.

## Dev Agent Record

### File List
- `execution/backend/app/models/company.py` (added `CompanyDomainAlias` model + relationship)
- `execution/backend/alembic/versions/002_domain_aliases.py` (new migration)
- `execution/backend/app/api/v1/admin.py` (added `POST /domain-alias` + `GET /domain-alias/{id}`)
- `execution/backend/app/services/scoring_service.py` (updated `_get_or_create_company()` for alias lookup)
- `execution/backend/tests/test_domain_aliases.py` (new unit tests)
- `docs/stories/sprint-status.yaml` (updated)

### Change Log
- **2026-02-05:** Implementation complete.
    - [x] AC1: Created `CompanyDomainAlias` model with `company_id`, `alias_domain`, `created_at` columns.
    - [x] AC2: Updated `_get_or_create_company()` to check alias table before creating new company.
    - [x] AC3: Created `POST /api/v1/admin/domain-alias` endpoint for alias registration.
    - [x] AC4: Created `GET /api/v1/admin/domain-alias/{company_id}` endpoint for listing aliases.
    - [x] Created Alembic migration and applied table to SQLite DB.
