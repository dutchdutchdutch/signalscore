---
id: 3-2
title: "Company Detail Page with Score Breakdown"
epic: "Epic 3: User Comparison & Context"
status: "done"
priority: "high"
estimate: "6h"
created: "2026-02-04"
sprint_theme: "User Experience - Minimal Usable Experience"
---

# Story 3.2: Company Detail Page with Score Breakdown

## Story

As a **user curious about a company's performance**,
I want to access a dedicated detail page for their Signal Score,
so that I can understand the specific categories, data sources, and methodology behind the rating.

## Acceptance Criteria

- [ ] **AC1: SEO-Friendly URLs & Page Accessibility**
  - Page accessible via unique URL using company domain: `/signal/[domain-slug]`
  - Examples: `/signal/www-nordstrom-com`, `/signal/www-stripe-com`
  - Users can bookmark and revisit URL directly without search
  - "Company Not Found" state when domain doesn't exist in database
  - Not Found page suggests navigating to home to request analysis

- [ ] **AC2: Core Data Consistency**
  - Display summary data from Score Card (Total Score, Company Name, Scored At date)
  - Maintain visual consistency with CompanyCard component
  - Reuse ScoreDisplay component for visual continuity

- [ ] **AC3: Category Breakdown & Transparency**
  - Primary focus: visualization of category scores
  - Categories: AI Keywords, Non-Eng AI Roles, Agentic Signals, Tool Stack, AI Platform Team
  - Each category includes description of what's evaluated
  - Disclaimer: "Scores derived from public data; internal company realities may differ"
  - Disclaimer is contextual (not an alert), integrated naturally

- [ ] **AC4: Signal Scale Reference**
  - "Signal Scale" reference section explaining the rating system
  - Show scale names (Transformational, High, Medium-High, Medium-Low, Low, No Signal)
  - Include example criteria for "Leading/Transformational" category

- [ ] **AC5: Methodology & Education**
  - Footer CTA/link to methodology blog post (placeholder URL for now)
  - "Signal Model Development and Scoring Philosophy" link
  - Placeholder links acceptable for layout purposes

## Tasks / Subtasks

- [x] **Task 1: Create dynamic route and page structure** (AC: 1)
  - [x] Create `/app/signal/[slug]/page.tsx` dynamic route
  - [x] Parse slug to extract domain (convert `www-stripe-com` → `www.stripe.com`)
  - [x] Query backend for company by domain/URL

- [x] **Task 2: Implement "Company Not Found" state** (AC: 1)
  - [x] Design not-found UI component
  - [x] Link to home page with CTA to request analysis
  - [x] Handle 404 gracefully (not a hard error page)

- [x] **Task 3: Build detail page header with score summary** (AC: 2)
  - [x] Reuse ScoreDisplay component
  - [x] Show company name, domain, scored_at date
  - [x] Maintain visual consistency with search results card

- [x] **Task 4: Create category breakdown section** (AC: 3)
  - [x] Display all component_scores with labels
  - [x] Add category descriptions (what each measures)
  - [x] Include contextual disclaimer about public data

- [x] **Task 5: Build Signal Scale reference section** (AC: 4)
  - [x] Create scale visualization or list
  - [x] Define criteria for each level
  - [x] Highlight company's current position

- [x] **Task 6: Add methodology footer** (AC: 5)
  - [x] Create footer section with methodology CTA
  - [x] Add placeholder links for blog posts
  - [x] Style as subtle, informational footer

- [x] **Task 7: Connect arrow navigation from CompanyCard** (AC: 1)
  - [x] Update CompanyCard to navigate to detail page on click
  - [x] Generate correct slug from company URL/domain

## Dev Notes

### URL Slug Format

Domain to slug conversion:
```
www.stripe.com → www-stripe-com
careers.google.com → careers-google-com
```

Slug to domain conversion (reverse):
```
www-stripe-com → www.stripe.com
```

### Backend API

May need new endpoint or query parameter:
- `GET /api/v1/companies?domain=www.stripe.com`
- Or use existing score lookup by company name

### Category Descriptions (Draft)

| Category | Description |
|----------|-------------|
| AI Keywords | Frequency of AI/ML terms in job postings |
| Agentic Signals | References to autonomous agents, workflows |
| Tool Stack | Modern AI/ML tools (TensorFlow, PyTorch, etc.) |
| Non-Eng AI Roles | AI roles outside engineering (Product, Design) |
| AI Platform Team | Dedicated AI infrastructure/platform teams |

### Signal Scale Reference

| Level | Score Range | Description |
|-------|-------------|-------------|
| Transformational | 4.5+ | Industry-leading AI adoption |
| High | 3.5-4.4 | Strong AI integration |
| Medium-High | 2.5-3.4 | Growing AI presence |
| Medium-Low | 1.5-2.4 | Early AI exploration |
| Low | 0.5-1.4 | Minimal AI signals |
| No Signal | <0.5 | No detectable AI activity |

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References
- Fixed `CompanyCard.tsx` corruption during edit.
- Fixed `SignalDetailPage` test case sensitivity for uppercase transformations.

### Completion Notes List
- Implemented `/signal/[slug]` page with requested breakdown and scale.
- Updated `CompanyCard` to wrap in `Link` for SEO-friendly navigation.
- Verified backend `get_score` supports domain lookups.
- Added comprehensive tests for new page and updated card tests.
- **Verification**: `npm run test:run` passes.

### File List
- execution/backend/app/api/v1/scores.py
- execution/frontend/src/app/signal/[slug]/page.tsx
- execution/frontend/src/app/signal/[slug]/__tests__/page.test.tsx
- execution/frontend/src/components/ui/CompanyCard.tsx
- execution/frontend/src/components/ui/ScoreDisplay.tsx
- execution/frontend/src/components/ui/__tests__/CompanyCard.test.tsx
- execution/frontend/src/components/ui/index.ts
- execution/backend/app/schemas/scores.py
