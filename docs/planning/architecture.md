---
stepsCompleted:
- step-01-init
- step-02-context
stepsCompleted:
- step-01-init
- step-02-context
- step-03-starter
stepsCompleted:
- step-01-init
- step-02-context
- step-03-starter
- step-04-decisions
stepsCompleted:
- step-01-init
- step-02-context
- step-03-starter
- step-04-decisions
- step-05-patterns
stepsCompleted:
- step-01-init
- step-02-context
- step-03-starter
- step-04-decisions
- step-05-patterns
- step-06-structure
- step-07-validation
- step-08-complete
status: 'complete'
completedAt: '2026-02-03'
inputDocuments:
- prd.md
- product-brief-signalscore-2026-02-03.md
workflowType: 'architecture'
project_name: 'signalscore'
user_name: 'User'
date: '2026-02-03'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
*   **Frontend (Next.js)**: Needs to handle Search (FR01), Score Display (FR02), Evidence visualization (FR03), and user submissions (FR05).
*   **Backend (Python)**: Must effectively scrape various sources (FR07, FR08), perform semantic scoring (FR09), and manage data freshness (FR10, FR12).
*   **Admin Tools**: Critical for manual overrides and scraper training (FR13-FR16), implying a need for an internal dashboard or admin API.

**Non-Functional Requirements:**
*   **SEO Performance**: SSR/SSG is non-negotiable for company profiles to ensure search visibility.
*   **Scraper Reliability**: The "Walking Skeleton" must prove value, requiring robust error handling and fallback mechanisms (FR-NFR).
*   **Rate Limiting**: Essential to protect the API and control costs (LLM usage).

**Scale & Complexity:**
*   **Primary Domain**: Web App (Data-Intensive/Search).
*   **Complexity Level**: Medium. The complexity lies in the *data acquisition and scoring logic*, not the user interface interaction.
*   **Estimated Architectural Components**: ~3-4 Core Containers (Frontend, API/Worker, Database, Cache/Queue).

### Technical Constraints & Dependencies
*   **Python Requirement**: Backend *must* be Python for ecosystem leverage (BeautifulSoup, Pandas, LangChain).
*   **SEO/Next.js**: Frontend *must* be Next.js for superior SEO capabilities.
*   **SQLite/Firebase MVP**: Initial infrastructure is constrained to validaton-friendly, low-cost options.

### Cross-Cutting Concerns Identified
*   **Scraping Strategy**: Affects data model, worker queues, and admin tools.
*   **Data Freshness**: Impacts caching strategy and background worker scheduling.
*   **Confidence Scoring**: Permeates the UI (display) and Domain Logic (calculation).

## System Diagrams

High-level visual representations of the system boundaries and containers.

### System Context (Level 1)
Describes the interaction between Users, SignalScore, and External Systems.
- [View Context Diagram](../../.agent/context/c4_context.mmd)

### Container Architecture (Level 2)
Describes the internal applications and services.
- [View Container Diagram](../../.agent/context/c4_container.mmd)

### Component Architecture (Level 3)
Describes the internal structure of the Backend Service (The Intelligence).
- [View Backend Component Diagram](../../.agent/context/c4_code.mmd)

> **Update (2026-02-05):** Diagrams updated to reflect "Subdomain Discovery" and "ATS Detection" modules added in Stories 4.3 & 4.4. The system now interacts directly with Company Ecosystems (Subdomains) independent of search engines.

## Starter Template Evaluation

### Primary Technology Domain
**Web Application (Decoupled Full-Stack)**: Next.js + Python.

### Starter Options Considered
*   **Vinta Next.js + FastAPI Template**: Best-in-class integration. Syncs types between Pydantic (Backend) and Zod (Frontend).
*   **FastAPI Fullstack (Tiangolo)**: Excellent, but biased towards React (SPA) rather than Next.js (SSR) in many configurations.
*   **Manual Setup**: Too slow for "Walking Skeleton".

### Selected Starter: Vinta Software Next.js + FastAPI Template (Modified)

**Rationale for Selection:**
It solves the hardest problem of decoupled apps: **Type Safety**. By bridging Pydantic and Zod, we ensure that if the Scraper schema changes, the Frontend build fails, preventing runtime errors.

**Initialization Strategy:**
We will use the template concepts but reorganize locally to match the project's folder structure preference.

**Architectural Decisions Provided by Starter:**

**Language & Runtime:**
*   Frontend: TypeScript (Next.js 14+)
*   Backend: Python 3.11+ (FastAPI)

**Code Organization (Customized):**
*   Root: `/` (Repository Root)
*   Execution Context: `/execution` (All runtime code)
*   Frontend: `/execution/frontend` (Next.js App Router)
*   Backend: `/execution/backend` (FastAPI application)

**Deployment Pipeline:**
*   **Source Control**: GitHub.
*   **CI/CD**: GitHub Actions (Standard for this template stack).
*   **Deployment Target**: Firebase (Frontend + Functions/Containers) or Google Cloud Run (Backend Containers).

**Development Experience:**
*   Hot Reload everywhere.
*   Pre-configured Linting (Eslint/Ruff).

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
*   **Database Engine**: SQLite (MVP) -> Postgres (Scale).
*   **Auth Provider**: Auth.js (Self-hosted) with simple "Admin" role claim.
*   **Inter-Service Protocol**: REST (Internal Docker Network).

**Important Decisions (Shape Architecture):**
*   **Type Sharing**: OpenAPI Auto-Generation (FastAPI -> TypeScript Client).
*   **Design System**: "System Minimal" (Tokens locked in `tokens.css`).

**Deferred Decisions (Post-MVP):**
*   **Vector Database**: Use Postgres `pgvector` later, but standard SQL for Phase 1a.
*   **Job Queue**: Python `asyncio` background tasks first; Celery/Redis later.

### Data Architecture

**ADR-001: Database Choice (SQLite -> Postgres)**
*   **Date**: 2026-02-03
*   **Decision**: Use **SQLite** for Phase 1a (MVP/Local), migrate to **Postgres** for Phase 1b (Production/Scale).
*   **Rationale**: Zero-config file-based DB allows "Walking Skeleton" to run anywhere immediately. Removes "Cloud SQL" setup tax for validation phase.
*   **Tools**: SQLAlchemy (Python) for ORM, Alembic for migrations (essential for the future switch).

### Authentication & Security

**ADR-002: Auth Strategy (Auth.js)**
*   **Date**: 2026-02-03
*   **Decision**: Use **Auth.js (NextAuth v5)** with "Stateless JWT" pattern.
*   **Rationale**: Python backend needs to trust tokens without calling external APIs (Clerk/Auth0) on every request to save cost/latency.
*   **Mechanism**: Next.js issues JWT. Python validates signature using shared `AUTH_SECRET` env var.
*   **Roles**: Simple `role: "admin"` claim added to JWT.

### API & Communication Patterns

**ADR-003: Backend-for-Frontend (BFF) & REST**
*   **Date**: 2026-02-03
*   **Decision**: Use **REST** over Internal Docker Network.
*   **Rationale**: GraphQL is overkill for this data model. Next.js Route Handlers (`/app/api/...`) act as the BFF, proxying requests to the hidden Python backend.
*   **Type Safety**: `npm run generate-client` pulls `openapi.json` from running Python server.

### Frontend Architecture

**ADR-004: Design System Implementation**
*   **Date**: 2026-02-03
*   **Decision**: **"System Minimal"** Custom Theme.
*   **Source of Truth**: `design-system/signalscore/theme.css`.
*   **Implementation**: Tailwind CSS configured to map utility classes (e.g., `bg-base`) to CSS variables. Component library (Shadcn/UI) customized to match strict "No Rounding / High Contrast" specs.

### Infrastructure & Deployment

**ADR-005: Deployment Targets**
*   **Date**: 2026-02-03
*   **Decision**: **Hybrid Serverless**.
*   **Local**: Docker Compose (Orchestration).
*   **Production Frontend**: Vercel / Firebase Hosting.
*   **Production Backend**: Google Cloud Run (Container).
*   **Production DB**: Neon (Serverless Postgres).

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
**3** critical areas where Python/JS conventions clash: Casing, Layouts, and Error Handling.

### Naming Patterns

**Casing Standards (The "Boundary Rule")**
*   **Database (SQL)**: `snake_case` (e.g., `users`, `is_active`).
*   **Backend (Python)**: `snake_case` for variables/functions.
*   **API (JSON)**: `camelCase` (Pydantic configured with `alias_generator=to_camel`).
*   **Frontend (TS)**: `camelCase` for variables/props.
*   **Components**: `PascalCase` (e.g., `SignalCard.tsx`).

**File Naming**
*   **Next.js**: `kebab-case` folders (e.g., `app/company-profile/[id]/page.tsx`).
*   **Python**: `snake_case` modules (e.g., `routers/company_router.py`).

### Format Patterns

**API Response Formats**
*   **Success**: Return data directly. No `{ data: ... }` wrapper unless pagination requires metadata.
*   **Errors**: RFC 7807 Problem Details.
    ```json
    {
      "type": "about:blank",
      "title": "Not Found",
      "status": 404,
      "detail": "Company with ID 123 not found"
    }
    ```

**Date Handling**
*   **Transport**: ISO 8601 Strings (`2023-10-27T14:00:00Z`).
*   **Frontend**: Display formatted (e.g., "Oct 27, 2023"). NEVER store/transport formatted strings.

### Process Patterns

**Error Handling**
*   **Backend**: Raise `HTTPException` in FastAPI. Do not return explicit error objects from services.
*   **Frontend**: Use `try/catch` in Server Actions. Use `error.js` boundaries for distinct UI sections (e.g., "Company Card failed to load").

**Loading States**
*   **React Suspense**: Prefer `<Suspense fallback={<Skeleton />}>` over `if (loading) return ...`.
*   **Skeletons**: Must match the dimensions of the "System Minimal" cards exactly to prevent layout shift.

### Enforcement Guidelines

**All AI Agents MUST:**
1.  **Respect the Casing Boundary**: Never leak `snake_case` into the Frontend props.
2.  **Use Semantic Colors**: Do not hardcode hex values. Use `bg-surface`, `text-primary`.
3.  **Strict Typing**: No `any` in TypeScript. No untyped `dict` in Python (use Pydantic).

## Project Structure & Boundaries

### Complete Project Directory Structure

```plaintext
signalscore/
├── .github/workflows/               # CI/CD Pipelines
├── data/                            # Local SQLite & Test Data (Volume Mounts)
├── design-system/
│   └── signalscore/
│       ├── theme.css                # DESIGN TRUTH
│       └── MASTER.md
├── diffs/                           # BMad Context (Auto-generated)
├── docs/                            # Documentation (PRD, Arch, Etc)
├── execution/                       # MAIN RUNTIME MONOREPO
│   ├── docker-compose.yml           # Orchestration
│   ├── backend/                     # PYTHON SERVICE
│   │   ├── Dockerfile
│   │   ├── pyproject.toml
│   │   ├── alembic/                 # Migrations
│   │   ├── app/
│   │   │   ├── main.py              # Entry
│   │   │   ├── core/                # Config, Logging
│   │   │   ├── models/              # SQLAlchemy Models (Snake Case)
│   │   │   ├── schemas/             # Pydantic (CamelCase Alias)
│   │   │   ├── api/                 # Env Routes
│   │   │   └── services/            # Scraping/Scoring Logic
│   │   └── tests/
│   └── frontend/                    # NEXT.JS SERVICE
│       ├── Dockerfile
│       ├── package.json
│       ├── next.config.js
│       ├── tailwind.config.ts       # Maps to theme.css
│       ├── components.json          # Shadcn Config
│       ├── src/
│       │   ├── app/                 # App Router (BFF)
│       │   │   ├── api/             # Route Handlers (Proxy)
│       │   │   └── (routes)/
│       │   ├── components/
│       │   │   ├── ui/              # Shadcn Primitives
│       │   │   └── features/        # Business Components
│       │   ├── lib/
│       │   │   ├── api-client/      # Generated TS Client
│       │   │   └── utils.ts
│       └── tests/
└── scripts/                         # Dev Utilities
    ├── setup.sh
    └── generate_client.sh           # OpenAPI Bridge Script
```

### Architectural Boundaries

**API Boundaries (The Air Gap)**
*   **Public -> Frontend**: HTTPS (Port 3000). Next.js App Router handles all user traffic.
*   **Frontend -> Backend**: HTTP (Port 8000). Internal Docker Network. *Not exposed to internet.*
*   **Authenticaton**: `AUTH_SECRET` shared via Environment Variable. Requests from Frontend to Backend must include `x-internal-secret` header.

**Requirements to Structure Mapping**
*   **Design System**: `design-system/theme.css` -> `frontend/tailwind.config.ts`.
*   **Scoring Engine (FR09)**: `execution/backend/app/services/score_engine.py`.
*   **Scrapers (FR07)**: `execution/backend/app/services/scrapers/`.
*   **Search UI (FR01)**: `execution/frontend/src/app/(routes)/page.tsx`.

### File Organization Patterns

**Source Organization**
*   **Frontend**: Feature-folded. `components/features/company-card/*` contains the component + sub-components.
*   **Backend**: Layered. `api` -> `services` -> `models`.

**Configuration Files**
*   **Env Vars**: `.env` at root (gitignored). Parsed by `docker-compose` and injected.
*   **Frontend Config**: `next.config.js` for headers/rewrites.

## Architecture Validation Results

### Coherence Validation ✅
*   **Decision Compatibility**: Python Backend + Next.js Frontend is a proven pattern. The explicit **OpenAPI Bridge** eliminates the biggest risk (type drift).
*   **Pattern Consistency**: The "Boundary Rule" regarding Casing (`snake_case` vs `camelCase`) is critical and well-documented.
*   **Structure Alignment**: The `/execution` monorepo structure supports the containerization strategy perfectly.

### Requirements Coverage Validation ✅
*   **Functional**: Search, Scoring, and Admin features map directly to specific directories (`services/scrapers`, `app/api`).
*   **Non-Functional**:
    *   *SEO*: Handled by Next.js SSR.
    *   *Performance*: "System Minimal" (No Blur/Glass) ensures fast rendering.
    *   *Reliability*: Docker Compose ensures "Walking Skeleton" reproducibility.

### Implementation Readiness Validation ✅
*   **Completeness**: High. We have defined the *look* (theme.css), the *shape* (OpenAPI), and the *logic* (Python).
*   **Gap Analysis**: CI/CD pipeline was implied. Added `.github/workflows/ci.yml` to structure.

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed
- [x] Scale and complexity assessed

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions (ADR-001 to ADR-005)
- [x] Technology stack fully specified (Next.js 14, Python 3.11, SQLite)

**✅ Implementation Patterns**
- [x] Naming conventions established (The Boundary Rule)
- [x] Structure patterns defined (Monorepo)
- [x] Communication patterns specified (REST + OpenAPI)

**✅ Project Structure**
- [x] Complete directory structure defined
- [x] Component boundaries established

### Architecture Readiness Assessment
**Overall Status:** READY FOR IMPLEMENTATION
**Confidence Level:** High


