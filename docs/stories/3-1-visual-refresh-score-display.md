---
id: 3-1
title: "Visual Refresh of Scoring Result Display"
epic: "Epic 3: User Comparison & Context"
status: "done"
priority: "high"
estimate: "3h"
created: "2026-02-04"
sprint_theme: "User Experience - Minimal Usable Experience"
---

# Story 3.1: Visual Refresh of Scoring Result Display

## Story

As a **user searching for a company's AI readiness**,
I want the signal score to be **immediately obvious and visually prominent** in the search results,
so that I can **instantly understand the core value** without cognitive effort.

## Context

The current implementation shows the score as a small badge next to the company name. This is the **primary value proposition** of SignalScore and needs to be the visual hero of the results display.

## Acceptance Criteria

- [x] **AC1**: Score is the dominant visual element in the result card
  - Score value (1-5) is displayed in a large, prominent format
  - Score is immediately visible without scanning
  - Visual weight ratio: Score should be ~3x larger than company name

- [x] **AC2**: Score category has clear visual differentiation
  - Category colors are vibrant and semantic (not muted badges)
  - Category label (e.g., "Transformational", "High", "Medium-High") is readable
  - Color palette uses existing scheme: high=green, medium_high=blue, medium_low=yellow, low=red, transformational=purple, no_signal=gray

- [x] **AC3**: Card layout emphasizes the score-first hierarchy
  - Score positioned as visual anchor (left or center)
  - Company name secondary but clearly readable
  - Domain/URL tertiary

- [x] **AC4**: Design works for all score categories
  - All 6 categories render correctly with distinct colors
  - No visual bugs at category boundaries (1-5 range)
  - "No Signal" case displays gracefully

- [x] **AC5**: Responsive behavior maintained
  - Works on mobile viewports (min-width: 320px)
  - Score remains prominent on all screen sizes

## Tasks / Subtasks

- [x] **Task 1: Design the new score display component** (AC: 1, 2)
  - [x] Create `ScoreDisplay.tsx` component for prominent score rendering
  - [x] Implement large numeric score with category ring/background
  - [x] Add category label with semantic color coding

- [x] **Task 2: Update CompanyCard layout** (AC: 3)
  - [x] Refactor `CompanyCard.tsx` to use new score-first layout
  - [x] Position ScoreDisplay as visual anchor
  - [x] Adjust typography hierarchy (score > name > domain)

- [x] **Task 3: Implement category color system** (AC: 2, 4)
  - [x] Define CSS variables or classes for each category
  - [x] Ensure sufficient contrast for accessibility
  - [x] Test all 6 categories visually

- [x] **Task 4: Handle edge cases** (AC: 4)
  - [x] Style "no_signal" state distinctly (gray, muted)
  - [x] Handle missing score data gracefully
  - [x] Test score-less company cards (backward compatibility)

- [x] **Task 5: Responsive design** (AC: 5)
  - [x] Test on 320px, 375px, 768px, 1024px viewports
  - [x] Adjust layout if needed for mobile

- [x] **Task 6: Add score date display** (AC: 3)
  - [x] Add `scored_at` field to backend `ScoreResponse` schema
  - [x] Update API endpoints to include score timestamp
  - [x] Display date in CompanyCard (day month year format)

- [x] **Task 7: Code review fixes** (Review follow-up)
  - [x] Fix uncaught exception in domain extraction with try/catch
  - [x] Fix placeholder circle size mismatch (80px → 96px)
  - [x] Add scored_at to pilot data (Feb 1, 2026)
  - [x] Remove unused imports from backend schema

## Testing Constraints

> [!IMPORTANT]
> **Use existing companies in the database for testing.** Do NOT trigger new analysis during development of this story. Query `/api/v1/companies` to get already-scored companies for visual testing.

## Dev Notes

### Current Implementation

**Files to modify:**
- `execution/frontend/src/components/ui/CompanyCard.tsx` - Main card with score badge
- `execution/frontend/src/components/ui/SearchResults.tsx` - Results container

**Current score display (lines 47-52 in CompanyCard.tsx):**
```tsx
{score && (
  <div className={`score-badge ${score.category}`}>
    <span className="score-value">{score.score}</span>
    <span className="score-label">{score.category_label}</span>
  </div>
)}
```

### ScoreResponse Schema (from schema.d.ts)
```typescript
ScoreResponse: {
  status: "completed";
  company_name: string;
  score: number;  // 1-5
  category: "high" | "medium_high" | "medium_low" | "low" | "transformational" | "no_signal";
  category_label: string;
  signals: SignalResponse;
  component_scores: ComponentScoresResponse;
  evidence: string[];
}
```

### Design Direction

**Option A: Large Circular Score (Recommended)**
- Big circular indicator with score number centered
- Category color as ring/fill
- Company info to the right

**Option B: Score-First Horizontal**
- Large numeric score left-aligned
- Category label below score
- Company info takes remaining space

### Existing Color Variables (from globals.css)
```css
--color-primary
--color-text-primary
--color-text-secondary
--color-surface-alt
--color-border
```

### Category Color Reference (from CompanyCard.tsx lines 134-168)
- `high`: green (rgba(34, 197, 94))
- `medium_high`: blue (rgba(59, 130, 246))
- `medium_low`: yellow (rgba(234, 179, 8))
- `low`: red (rgba(239, 68, 68))
- `transformational`: purple (rgba(147, 51, 234))
- `no_signal`: gray (rgba(107, 114, 128))

### Project Structure Notes

- Using styled-jsx for component styles (not Tailwind classes except for utility)
- Design system: "System Minimal" with custom tokens
- Component location: `execution/frontend/src/components/ui/`

### References

- [Source: execution/frontend/src/components/ui/CompanyCard.tsx - Current implementation]
- [Source: execution/frontend/src/lib/api-client/schema.d.ts#ScoreResponse - Data shape]
- [Source: docs/planning/architecture.md#AR07 - Design System]

## Dev Agent Record

### Agent Model Used

Gemini 2.5 Pro

### Debug Log References

- Fixed score overflow by increasing circle from 80px to 96px, reducing font from 36px to 26px
- Added 8px padding inside score circle for breathing room

### Completion Notes List

- Created `ScoreDisplay.tsx` with large circular indicator and vibrant category colors
- Refactored `CompanyCard.tsx` with score-first layout (score left, company info right)
- Implemented all 6 category color mappings with semantic colors
- Added placeholder display for companies without scores
- Implemented responsive design with mobile breakpoints at 480px

### File List

- `execution/frontend/src/components/ui/ScoreDisplay.tsx` (NEW)
- `execution/frontend/src/components/ui/CompanyCard.tsx` (MODIFIED)
- `execution/frontend/src/components/ui/index.ts` (MODIFIED)
- `execution/frontend/src/lib/api-client/schema.d.ts` (MODIFIED)
- `execution/backend/app/schemas/scores.py` (MODIFIED)
- `execution/backend/app/api/v1/scores.py` (MODIFIED)
