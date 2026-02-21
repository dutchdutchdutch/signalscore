---
stepsCompleted:
- step-01-validate-prerequisites
- step-02-design-epics
inputDocuments:
- docs/planning/prd.md
- docs/planning/architecture.md
---

# SignalScore - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for SignalScore, decomposing the requirements from the PRD, UX Design if it exists, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR01: User can search for a company by Name or URL, receiving instant feedback if the company is indexed or not.
FR02: User can view a company's "AI Readiness Score" (1-5 Level) clearly displayed on the profile.
FR03: User can view the detailed "Evidence List" justifying the score, including specific positive/negative signals found.
FR04: User can see the "Confidence Level" (High/Medium/Low) of the score based on data density/quality.
FR05: User can submit a request to "Add a Company" if it is missing from the index, which queues it for the scraping pipeline (Phase 1b).
FR06: User can switch between "Job Seeker" view (Risk focus) and "Benchmarker" view (Comparison focus).
FR07: System can ingest and parse content from public URLs (Careers Pages, Engineering Blogs, 10-K Filings, Press Releases).
FR08: System can vary scraping strategy based on site type (e.g. Greenhouse embedding vs standard HTML).
FR09: System can identify and classify specific "AI Roles" (e.g. LLM Engineer, Agent Orchestrator) vs "Legacy Roles" using keyword/semantic matching.
FR10: System can extract and validate "Public Activity" timestamps (e.g. Last tech blog post date) to ensure freshness.
FR11: System allows "Missing Data" (e.g. no blog found) to be weighed as a negative signal in the scoring algorithm.
FR12: System automatically expires/invalidates signals older than 12 months.
FR13: Admin can manually override a calculated score and attach a "Correction Reason" for audit trails.
FR14: Admin can view "Scraper Failures" and manually map URL patterns to fix extraction issues (Self-Annealing).
FR15: Admin can trigger a manual "Re-Score" for a specific company to force an update.
FR16: Admin can upload "Ground Truth" datasets to validate scoring accuracy against reference companies.
FR17: User can view System & Container diagrams (Architecture Context).

### NonFunctional Requirements

NFR1: Time to Interactive: <1.5s (Core Web Vitals "Good" threshold) on Company Profile pages.
NFR2: Score Latency: Cached scores must load in <200ms.
NFR3: Scraper Success Rate: >80% of "Top 50" careers pages must be scrapable without human intervention.
NFR4: Freshness: All scores are re-calculated automatically every 30 days.
NFR5: Rate Limiting: Public API/Search limited to 10 requests/minute per IP.
NFR6: Polite Scraping: Scrapers must respect `robots.txt` and implement aggressive caching (min 24h).
NFR7: Data Rights: Analysis strictly limited to publicly available URLs. No "leaked" data.
NFR8: Disclaimer: Distinct "For Informational Purposes Only" disclaimer visible on all scores.
NFR9: Sitemap: Auto-generated `sitemap.xml` for all "Scored Companies" must update within 24h of ingestion.
NFR10: Metadata: Dynamic OpenGraph images for social sharing (e.g. "Stripe - AI Readiness: 5/5").

### Additional Requirements

From Architecture:
- AR01: Technology Stack: Next.js 14+ (Frontend) and Python 3.11+ FastAPI (Backend).
- AR02: Infrastructure: Hybrid Serverless deployment (Vercel + Cloud Run), Docker Compose for local orchestration.
- AR03: Database: SQLite for MVP (Phase 1a) with migration path to Postgres (Phase 1b).
- AR04: Authentication: Auth.js with Stateless JWT pattern (BFF).
- AR05: API Communication: REST over Internal Docker Network for Backend-Frontend communication.
- AR06: Type Safety: OpenAPI Bridge (FastAPI -> TypeScript Client) must be implemented.
- AR07: Design System: "System Minimal" implementation using custom Tailwind tokens mapped to `design-system/signalscore/theme.css`.
- AR08: Casing Standards: Strict enforced boundaries (snake_case DB/Python, camelCase API/JS).
- AR09: Project Structure: Monorepo structure under `/execution` (frontend, backend, docker-compose).
- AR10: External Service Integration: Integration with LLM providers for scoring logic.

### FR Coverage Map

FR01: Epic 1 - Search functionality.
FR02: Epic 2 - Score Display.
FR03: Epic 2 - Evidence List.
FR04: Epic 2 - Confidence Level.
FR05: Epic 4 - User Submissions (Queue).
FR06: Epic 3 - View Modes.
FR07: Epic 1 - Base Scraping.
FR08: Epic 1 - Scraping Strategies.
FR09: Epic 2 - Role Classification.
FR10: Epic 2 - Timestamp Validation.
FR11: Epic 2 - Missing Data Logic.
FR12: Epic 2 - Data Expiration.
FR13: Epic 4 - Manual Override.
FR14: Epic 4 - Scraper Failures.
FR15: Epic 4 - Manual Re-Score.
FR16: Epic 4 - Ground Truth.
FR17: Epic 5 - Diagrams (Context).

## Epic List

### Epic 1: Foundation & Search (The "Walking Skeleton")
Establish the core technical stack (Next.js/Python/SQLite) and implement the end-to-end flow where a user can search for a company and effective scraping occurs.
**FRs covered:** FR01, FR07, FR08, AR01-AR10

### Epic 2: Core Scoring Engine & Evidence (The "Value Prop")
Implement the intelligence layer: deep semantic analysis, scoring algorithms, and the visualization of evidence (signals) and confidence levels.
**FRs covered:** FR02, FR03, FR04, FR09, FR10, FR11, FR12

### Epic 3: User Comparison & Context (The "Decision Tool")
Enhance the user experience with specific modalities (Job Seeker Risk vs Benchmarker) and performance optimizations.
**FRs covered:** FR06, NFR1, NFR2

### Epic 4: Admin Operations & Self-Annealing (The "Scale")
Build the operational tools that allow the system to scale and self-correct, including manual overrides, failure handling, and user submissions.
**FRs covered:** FR05, FR13, FR14, FR15, FR16

### Epic 5: SEO & Production Hardening (The "Launch")
Finalize the application for public release with SEO, diagrams, rate limiting, and compliance features.
**FRs covered:** FR17, NFR5-NFR10

### Epic 6: Alpha Deployment & Data Sync (The "Ship It")
Deploy the application to Google Firebase for alpha testing and implement bidirectional data sync so scoring data can be pushed from local to remote and pulled from remote to local, avoiding redundant LLM/scraping costs.
**Stories:**
- **6-1**: Firebase Alpha Deployment — GitHub Actions pipeline auto-deploys frontend (Firebase Hosting) + backend (Cloud Run) + remote DB on push to `main`.
- **6-2**: Push Local Scoring Data to Remote — CLI command to upsert local companies/scores/sources/aliases to the deployed environment.
- **6-3**: Pull Scoring Data from Remote to Local — CLI command to pull remote data back to local SQLite for development and debugging.

{{epics_list}}
