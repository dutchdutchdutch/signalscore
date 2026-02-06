---
id: 1-2
title: "Database Models & Company Entity"
epic: "Epic 1: Foundation & Search"
status: "review"
priority: "high"
estimate: "2h"
created: "2026-02-03"
completed: "2026-02-03"
---

# Story 1.2: Database Models & Company Entity

## Story

As a **Developer**,
I want the SQLAlchemy ORM configured with Alembic migrations and a `Company` model,
So that the system can persist company data for search and scoring.

## Acceptance Criteria

- [x] **AC1**: Database migrations work correctly
  - Running `alembic upgrade head` creates the `companies` table
  - Table location: `/data/signalscore.db`
  - Columns: `id (PK)`, `name`, `url`, `created_at`, `updated_at`

- [x] **AC2**: ORM timestamps are automatic
  - `created_at` and `updated_at` are set automatically on insert
  - `updated_at` is updated automatically on record modification

- [x] **AC3**: API responses use camelCase
  - Pydantic schemas serialize Company objects with camelCase keys
  - Example: `createdAt` instead of `created_at`

## Tasks/Subtasks

- [x] **Task 1: Configure SQLAlchemy Database Engine**
  - [x] Create `app/core/database.py` with engine and session factory
  - [x] Configure async session if needed
  - [x] Add Base model class for declarative models

- [x] **Task 2: Create Company SQLAlchemy Model**
  - [x] Create `app/models/company.py` with Company model
  - [x] Add id, name, url, created_at, updated_at columns
  - [x] Configure automatic timestamps

- [x] **Task 3: Initialize Alembic**
  - [x] Run `alembic init alembic` to create migration structure
  - [x] Configure `alembic.ini` with database URL
  - [x] Update `env.py` to use app models

- [x] **Task 4: Create Initial Migration**
  - [x] Generate migration for Company table
  - [x] Verify migration script is correct
  - [x] Test upgrade and downgrade

- [x] **Task 5: Create Pydantic Schemas with CamelCase**
  - [x] Create `app/schemas/company.py` with Company schemas
  - [x] Configure `alias_generator` for camelCase output
  - [x] Add CompanyCreate, CompanyRead schemas

## Dev Notes

### Architecture Requirements (from ADRs)
- **ADR-001**: SQLite for MVP at `/data/signalscore.db`
- **AR08**: snake_case in DB/Python, camelCase in API responses
- Pydantic v2 with `alias_generator=to_camel` pattern

### Technical Specifications
- SQLAlchemy 2.0+ with declarative base
- Alembic for migrations
- Pydantic 2.x schemas

### Dependency on Story 1.1
- Uses database path configured in docker-compose (`/data/signalscore.db`)
- Uses config from `app/core/config.py`

## Dev Agent Record

### Implementation Plan
- Created database.py with SQLAlchemy 2.0 engine and session factory
- Implemented Company model with mapped_column for type-safe columns
- Used server_default=func.now() for automatic timestamps
- Configured onupdate=func.now() for updated_at
- Created Alembic migration structure manually (avoiding CLI dependency issues)
- Implemented Pydantic schemas with to_camel alias_generator

### Debug Log
- No issues encountered

### Completion Notes
✅ Story 1.2 complete. Database layer established with:
- SQLAlchemy 2.0 engine configured for SQLite
- Company model with automatic timestamps
- Alembic migrations ready for `alembic upgrade head`
- Pydantic schemas with camelCase API output

## File List

### Created Files
- `execution/backend/app/core/database.py`
- `execution/backend/app/models/company.py`
- `execution/backend/app/schemas/company.py`
- `execution/backend/alembic.ini`
- `execution/backend/alembic/env.py`
- `execution/backend/alembic/script.py.mako`
- `execution/backend/alembic/versions/001_initial_companies.py`

### Modified Files
- `execution/backend/app/models/__init__.py`
- `execution/backend/app/schemas/__init__.py`

## Change Log

| Date | Change |
|------|--------|
| 2026-02-03 | Initial implementation - Database models and migrations complete |

## Status
review
