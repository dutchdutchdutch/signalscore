---
id: 3-7
title: "Bug: Inconsistent Signal Score References and Numbers"
epic: "Epic 3: User Comparison & Context"
status: "ready-for-dev"
priority: "high"
estimate: "1h"
created: "2026-02-04"
sprint_theme: "User Experience - Minimal Usable Experience"
---

# Story 3.7: Bug: Inconsistent Signal Score References and Numbers

## Story

As a **User**,
I want **the Signal Scale reference on the detail page to match the system's actual scoring model (0-100)**,
so that **I don't get confused by conflicting scales (0-100 vs 1-5) and terminology**.

## Acceptance Criteria

- [ ] **AC1: Scale Consistency (0-100)**
  - The "Signal Scale Reference" section uses the 1-100 point scale (not 1-5).
  - The ranges roughly align with:
    - 95-100
    - 80-94
    - 60-79
    - 30-59
    - 0-29

- [ ] **AC2: Label Consistency**
  - Section title: "Signal Score Reference".
  - Labels must match the Company Result Card (and User Request):
    - Transformational
    - Leading
    - Operational (Note: Verify if this maps to 'On Par')
    - Lagging (Note: Verify mapping for 'Trailing')
    - No Signal

## Tasks / Subtasks

- [ ] **Task 1: Update CONSTANTS in page.tsx** (AC: 1, 2)
  - [ ] Modify `SIGNAL_SCALE` constant in `execution/frontend/src/app/signal/[slug]/page.tsx`.
  - [ ] Update labels to: Transformational, Leading, Operational, Lagging, No Signal.
  - [ ] Update ranges to: 95-100, 80-94, 60-79, 30-59, 0-29.
  - [ ] Update descriptions to match the new levels.

- [ ] **Task 2: Verify Color Mapping** (AC: 2)
  - [ ] Ensure `categoryColors` in `ScoreDisplay.tsx` supports these new keys if the component relies on them for the *reference list* rendering (it currently uses `item.level` as key).
  - [ ] If `item.level` in the reference list is just for display, ensure it maps to a valid color key or update `categoryColors`.

## Dev Notes

- Current `SIGNAL_SCALE` in `page.tsx` uses: `transformational`, `high`, `medium_high`, `medium_low`, `low`, `no_signal`.
- Need to align this with the user's requested "Operational", "Lagging" terminology.
- `ScoreDisplay.tsx` exports `categoryColors` which keys off the *backend* enum values (e.g. `medium_low`).
- **Careful**: The reference list in `page.tsx` iterates over `SIGNAL_SCALE` and tries to look up colors in `categoryColors[item.level]`.
- We might need to map the *Display Label* (Operational) to the *Backend Category* (on_par/medium_high?) to get the right color, OR update the visual scale independently.

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

### File List
