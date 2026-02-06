# Story 5-6: Add Article Page (Scoring Methodology)

## Status
- **Status:** done
- **Priority:** Medium
- **Effort:** Medium

## Story
**As a** User (Investor, Employee, Job Seeker),
**I want** to read a detailed explanation of the SignalScore methodology and its underlying assumptions,
**So that** I can understand how the scores are derived and trust the results.

## Context
Currently, the footer is inconsistent across pages, and there is no dedicated place to explain the deep details of the scoring model. We need a "Scoring Methodology" article that is accessible from the footer. Ideally, this content should be single-sourced so it can be viewed as a styled web page AND as a standard Markdown file on GitHub.

## Acceptance Criteria

### AC1: Consistent Footer
**Given** any page in the application,
**When** the user scrolls to the bottom,
**Then** they should see a consistent footer with a link to "Methodology" (or "How it Works").

### AC2: Article Page (Web)
**Given** the user clicks the "Methodology" link,
**When** the page loads,
**Then** it should render the article content using the application's design system (layout, typography, dark mode support).

### AC3: Single Source of Truth
**Given** the article content,
**When** it updates,
**Then** it should update both the web view and be readable as a standalone file in the repo (e.g., on GitHub).

## Technical Notes
- **Content Source**: Likely a Markdown file (e.g., `docs/articles/scoring-methodology.md`) or a MDX file.
- **Rendering**: Use `react-markdown` or Next.js MDX support to render the content in the `app/article/[slug]` or `app/methodology` route.
- **Footer**: Refactor `page.tsx` footer into a reusable `<Footer />` component.

## Tasks
- [x] **Frontend**
    - [x] Create/Update `<Footer />` component.
    - [x] Create Article content source (Markdown).
    - [x] Implement Article Page (`/methodology`) with Markdown rendering.
    - [x] Ensure proper styling (prose, typography plugin).

## Dev Agent Record

### File List
- `execution/frontend/src/components/ui/Footer.tsx`
- `execution/frontend/src/app/methodology/page.tsx`
- `execution/frontend/src/lib/markdown.ts`
- `docs/articles/scoring-methodology.md`
- `execution/frontend/src/app/page.tsx`
- `execution/frontend/src/app/signal/[slug]/page.tsx`
- `execution/frontend/tailwind.config.js`
- `execution/frontend/src/lib/mock-data.ts`
- `execution/frontend/package.json`

### Change Log
- Created reusable `<Footer />` component and integrated it into Home and Signal pages.
- Created `scoring-methodology.md` as the single source of truth for methodology content.
- Implemented `/methodology` page using `react-markdown` and `@tailwindcss/typography` to render the article.
- Fixed build error in `mock-data.ts` by adding missing `domain` property.
