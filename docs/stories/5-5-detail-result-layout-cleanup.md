# Story 5-5: Detail Result Layout Cleanup

## Status
- **Status:** ready-for-dev
- **Priority:** Medium
- **Effort:** Small

## Story
**As a** User,
**I want** the category breakdown table to be compact and easy to scan,
**So that** I can quickly compare scores without excessive scrolling or eye-strain.

## Context
The recent addition of "Source Labels" (tags) to the breakdown table has negatively impacted readability:
1.  **Vertical Heigh**: Rows are too tall because tags wrap.
2.  **Horizontal Squeeze**: The Source column takes space, narrowing the Description column.
3.  **Scannability**: It is hard to compare scores at a glance.

## Acceptance Criteria

### AC1: Compact Vertical Height
**Given** a category row,
**When** displayed,
**Then** it should maintain a minimal consistent height (avoiding excessive wrapping).

### AC2: Readable Descriptions
**Given** the table layout,
**When** viewing the Description column,
**Then** it should have sufficient width to be legible.

### AC3: Source Access
**Given** the source tags are removed/minimized,
**When** the user interacts (hover/click),
**Then** they can still access the source attribution data.

## Technical Notes
- **Component**: `execution/frontend/src/app/signal/[slug]/page.tsx`
- **Current State**: Sources are inline tags in a 20% width column.

## Tasks
- [x] **Frontend**
    - [x] Refactor Table Layout (Select Design Option).
    - [x] Implement layout changes (Tooltip Layout).
    - [x] Verify responsiveness.

## Dev Agent Record

### File List
- `execution/frontend/src/app/signal/[slug]/page.tsx`

### Change Log
- Refactored category breakdown table to single-row layout.
- Implemented tooltip-based source display.
- Updated source labels ("Manual Rescore" -> "URL Submission").
- Added distinct empty states ("Not found" vs "Standard scan").
