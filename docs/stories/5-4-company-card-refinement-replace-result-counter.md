# Story 5-4: Company Card Refinement - Replace Result Counter

## Status
- **Status:** done
- **Priority:** Low
- **Effort:** Extra Small

## Story
**As a** User,
**I want** to see a clean search result list,
**So that** I am not distracted by redundant information ("1 Result").

## Context
Currently, the search results page always shows "X Results" at the top. If there is only 1 result (the expected case for 99% of searches), this header adds clutter. We should only show it if multiple results are returned (e.g., mergers/acquisitions).

## Acceptance Criteria

### AC1: Single Result = No Header
**Given** the search returns exactly 1 company,
**When** the results are displayed,
**Then** the "1 Result" header/counter is HIDDEN.
- The company card should appear directly.

### AC2: Multiple Results = Show Header
**Given** the search returns 2 or more companies,
**When** the results are displayed,
**Then** the "X Results" header acts as a divider/context.

### AC3: Alignment
**Given** the header is hidden,
**When** the single card is shown,
**Then** the layout spacing remains balanced.

## Technical Notes
- **Component**: `execution/frontend/src/components/ui/SearchResults.tsx`
- **Logic**: Check `results.length > 1`.

## Tasks
- [x] **Frontend**
    - [x] Add conditional rendering to `results-header` (`results.length > 1`).
    - [x] Verify styling when header is missing (Spacing preserved).

## Dev Agent Record

### File List
- `execution/frontend/src/components/ui/SearchResults.tsx` (Added conditional header logic)

### Change Log
- **2026-02-06**: Implemented Conditional Result Counter.
    - [x] AC1: Header hidden for single result.
    - [x] AC2: Header visible for multiple results.
    - [x] AC3: Layout remains balanced.
