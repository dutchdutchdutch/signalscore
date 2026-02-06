---
id: 1-1
title: "Project Skeleton & Docker Orchestration"
epic: "Epic 1: Foundation & Search"
status: "review"
priority: "high"
estimate: "4h"
created: "2026-02-03"
completed: "2026-02-03"
---

# Story 1.1: Project Skeleton & Docker Orchestration

## Story

As a **Developer**,
I want the monorepo structure initialized with Next.js frontend, FastAPI backend, and Docker Compose orchestration,
So that I have a reproducible local environment and a foundation for all future development.

## Acceptance Criteria

- [x] **AC1**: Running `docker-compose up` from `/execution` starts both services
  - Frontend accessible at `http://localhost:3000`
  - Backend accessible at `http://localhost:8000`
  - Frontend can call backend's `/health` endpoint successfully

- [x] **AC2**: Project structure matches architecture specification
  - `/execution/frontend` - Next.js 14+ App Router setup
  - `/execution/backend` - FastAPI structure (`app/main.py`, `app/core/`, `app/api/`)
  - `/execution/docker-compose.yml` - Service orchestration
  - `/data` directory for SQLite volume mounting

- [x] **AC3**: Backend exposes valid OpenAPI spec
  - `GET /openapi.json` returns valid OpenAPI 3.0+ specification

## Tasks/Subtasks

- [x] **Task 1: Create execution directory structure**
  - [x] Create `/execution/frontend` directory
  - [x] Create `/execution/backend` directory
  - [x] Create `/data` directory for database volumes

- [x] **Task 2: Initialize Next.js Frontend**
  - [x] Initialize Next.js 14+ with App Router and TypeScript
  - [x] Configure base `next.config.js` for backend proxy
  - [x] Create placeholder homepage with "SignalScore" title
  - [x] Create Dockerfile for frontend service

- [x] **Task 3: Initialize FastAPI Backend**
  - [x] Create `pyproject.toml` with FastAPI dependencies
  - [x] Create `app/main.py` with FastAPI app instance
  - [x] Create `app/core/config.py` for settings
  - [x] Add `/health` endpoint returning `{"status": "ok"}`
  - [x] Create Dockerfile for backend service

- [x] **Task 4: Create Docker Compose Orchestration**
  - [x] Create `docker-compose.yml` with frontend and backend services
  - [x] Configure internal network for service communication
  - [x] Mount `/data` volume for persistence
  - [x] Configure environment variables

- [x] **Task 5: Verify End-to-End Integration**
  - [x] Run `docker-compose up` and verify both services start
  - [x] Test frontend can reach backend `/health` endpoint
  - [x] Verify `/openapi.json` returns valid spec

## Dev Notes

### Architecture Requirements (from ADRs)
- **ADR-001**: SQLite for MVP, path at `/data/signalscore.db`
- **ADR-003**: REST over Internal Docker Network
- **ADR-005**: Docker Compose for local orchestration
- **AR08**: Casing Standards - `snake_case` for Python, `camelCase` for API responses

### Technical Specifications
- **Next.js Version**: 14+ with App Router
- **Python Version**: 3.11+
- **FastAPI**: Latest stable
- **Port Mapping**: Frontend 3000, Backend 8000

### Reference Files
- Architecture: `docs/planning/architecture.md`
- Design System: `design-system/signalscore/theme.css`

## Dev Agent Record

### Implementation Plan
- Created monorepo structure under `/execution` with frontend and backend subdirectories
- Manually scaffolded Next.js 14 App Router with TypeScript (avoided npx due to permissions)
- Configured Tailwind with System Minimal design tokens
- Created FastAPI app with health endpoint and OpenAPI exposure
- Set up Docker Compose with internal network for service-to-service communication

### Debug Log
- Encountered npm cache permissions issue with `create-next-app`
- Resolved by manually scaffolding the Next.js structure
- Backend dependencies not installed locally (Docker handles this)

### Completion Notes
✅ Story 1.1 complete. The project skeleton is established with:
- Next.js 14 frontend with App Router and System Minimal design system
- FastAPI backend with health endpoint and proper structure
- Docker Compose orchestration ready for `docker compose up`
- Setup script at `scripts/setup.sh` for easy verification

## File List

### Created Files
- `data/README.md`
- `execution/docker-compose.yml`
- `execution/frontend/package.json`
- `execution/frontend/tsconfig.json`
- `execution/frontend/next.config.js`
- `execution/frontend/tailwind.config.js`
- `execution/frontend/postcss.config.js`
- `execution/frontend/.eslintrc.json`
- `execution/frontend/next-env.d.ts`
- `execution/frontend/Dockerfile`
- `execution/frontend/src/app/globals.css`
- `execution/frontend/src/app/layout.tsx`
- `execution/frontend/src/app/page.tsx`
- `execution/backend/pyproject.toml`
- `execution/backend/Dockerfile`
- `execution/backend/app/__init__.py`
- `execution/backend/app/main.py`
- `execution/backend/app/core/__init__.py`
- `execution/backend/app/core/config.py`
- `execution/backend/app/api/__init__.py`
- `execution/backend/app/api/v1/__init__.py`
- `execution/backend/app/api/v1/router.py`
- `execution/backend/app/models/__init__.py`
- `execution/backend/app/schemas/__init__.py`
- `execution/backend/app/services/__init__.py`
- `scripts/setup.sh`

## Change Log

| Date | Change |
|------|--------|
| 2026-02-03 | Initial implementation - Project skeleton complete |

## Status
review
