---
id: 3-6
title: "Bug: Created At Date Missing from Company Card"
epic: "Epic 3: User Comparison & Context"
status: "ready-for-dev"
priority: "high"
estimate: "1h"
created: "2026-02-04"
sprint_theme: "User Experience - Minimal Usable Experience"
---

# Story 3.6: Bug: Created At Date Missing from Company Card

## Story

As a **User**,
I want **to see the 'Scored At' date on the company card in search results**,
so that **I know how fresh the score is without clicking into details**.

## Acceptance Criteria

- [ ] **AC1: Date Visibility**
  - The "Scored: [Date]" label is visible on the Company Card in the search results list.
  - The date is displayed under the search box (or within the card in the list).
  - Format matches the detail page: `DD MMM YYYY` (e.g., 14 Oct 2023).
  - Handles missing date gracefully (though scored companies should have dates).

## Tasks / Subtasks

- [ ] **Task 1: Verify data flow** (AC: 1)
  - [ ] Check if `scored_at` is correctly returned in the `ScoreResponse` for the search list.
  - [ ] Verify `CompanyCard` receives the `score` object prop correctly in `SearchResults`.
- [ ] **Task 2: Fix CompanyCard rendering** (AC: 1)
  - [ ] Ensure `scored_at` conditional rendering is working.
  - [ ] Check for CSS/Layout issues hiding the element.
  - [ ] Align date format with `SignalDetailPage` (already set to en-GB).

## Dev Notes

- `CompanyCard.tsx` already has logic for `score.scored_at`.
- Suspect `scored_at` field might be missing from the API response for the *list/search* view, or `SearchResults.tsx` isn't passing it through.
- Check `execution/backend/app/schemas/scores.py` and `execution/frontend/src/components/features/CompanySearch.tsx`.

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

### File List
