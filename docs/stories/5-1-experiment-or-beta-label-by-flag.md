# Story 5-1: Experiment/Beta Label Display

## Status
- **Status:** done
- **Priority:** Medium
- **Effort:** Extra Small

## Story
**As a** Product Owner,
**I want** to display an "Experimental" or "Beta" label in the top-right corner of the application,
**So that** users are aware that the application is in an early stage and results may change.

## Context
The application is evolving rapidly. We want to set user expectations without blocking functionality. The label should be easily configurable or removable as the product matures.

## Acceptance Criteria

### AC1: Label Configuration
**Given** the application configuration (ENV or Config file),
**When** I set `NEXT_PUBLIC_APP_STAGE` to "experimental", "beta", or empty,
**Then** the UI reflects the corresponding text.

### AC2: Visual Placement
**Given** the label is active,
**When** I view any page,
**Then** the label appears in the top-right corner (fixed or absolute position), distinct from the main navigation but clearly visible.
- Style: Subtle badge or sash.

### AC3: CSS-Only/Minimal Update
**Given** I want to change the text or remove it,
**When** I update the config and redeploy,
**Then** the change is reflected immediatey without complex code refactoring.

## Technical Notes
- **Frontend**: Next.js (App Router).
- **Component**: Create a global `StageLabel` component in `layout.tsx`.
- **Config**: Use `process.env.NEXT_PUBLIC_APP_STAGE` or a simple constant in `execution/frontend/src/config/site.ts` (if exists) or new config file.
- **Styling**: Tailwind CSS.

## Tasks
- [x] **Frontend**
    - [x] Define configuration strategy (ENV vs constant).
    - [x] Implement label logic (switched to inline text per user request).
    - [x] Update `page.tsx`.

## Dev Agent Record

### File List
- `execution/frontend/src/app/page.tsx` (Inline logic)
- `execution/frontend/next.config.js` (Env fallback)
- `execution/frontend/.env.local` (Local config)

### Change Log
- **2026-02-05**: Implemented inline "Experiment" label.
    - [x] AC1: Configured `NEXT_PUBLIC_APP_STAGE` logic.
    - [x] AC2: Implemented inline text in Hero description instead of top-right badge (User Request).
    - [x] AC3: Config-driven visibility.

