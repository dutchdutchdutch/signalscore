# Story 4.1: Deep Discovery Agent

Status: ready-for-dev

## Story

As a **User**,
I want the system to **automatically discover relevant signal sources (Engineering Blogs, GitHub Orgs, Tech Stacks)**,
so that the scoring is **thorough and based on deep research, not just a homepage scan.**

## Context

Currently, the system only scans the URL provided by the user. If the user provides `stripe.com`, we miss `stripe.com/blog/engineering` or `github.com/stripe`. This leads to low confidence scores and requires manual user work.

## Acceptance Criteria

1.  **AC1: Multi-Source Discovery**
    -   System automatically finds "secondary" URLs for a given company domain.
    -   Target sources:
        -   Engineering Blog / Tech Blog
        -   GitHub Organization
        -   Careers Page (if different from main domain)
        -   Developer Documentation / API Docs

2.  **AC2: Search Strategy**
    -   Implement a search capability (e.g., via Google Custom Search API or DuckDuckGo crawler) to find these specific signal sources.
    -   Query patterns: `site:stripe.com "engineering blog"`, `stripe github`, `stripe careers`.

3.  **AC3: Persistence**
    -   Store discovered sources in the `Company` model (e.g., a new `sources` JSON field or related table).
    -   Display discovered sources on the Company Detail page (read-only for now).

4.  **AC4: Failover**
    -   If no secondary sources are found, fallback gracefully to just the provided URL.
    -   Log "Discovery Failed" events for analysis.

## Tasks / Subtasks

-   [ ] **Task 1: Infrastructure Setup**
    -   [ ] Add `googlesearch-python` or configured Custom Search API client.
    -   [ ] Add `sources` field to `Company` database model (`List[str]` or `List[SourceObj]`).

-   [ ] **Task 2: Implement Discovery Service**
    -   [ ] Create `DiscoveryService` class.
    -   [ ] Implement search logic for key patterns (Blog, GitHub, Careers).
    -   [ ] Implement filtering/validation (ensure GitHub link is an org, not a random repo).

-   [ ] **Task 3: Output Integration**
    -   [ ] Update `Company` schema to return discovered sources.
    -   [ ] Update `CompanyCard` or `SignalDetailPage` to list "Sources Analyzed".

## Dev Notes

-   **Search API:**
    -   Option A: `googlesearch-python` (unofficial, easy for prototype, rate limits).
    -   Option B: Google Programmable Search Engine (official, 100 free/day).
    -   *Decision:* Start with Option A or a robust scraper fallback if rate limited.

-   **Data Model:**
    -   `sources`: `[{ "type": "github", "url": "..." }, { "type": "blog", "url": "..." }]`

## Dev Agent Record

### Agent Model Used

Antigravity

### File List
