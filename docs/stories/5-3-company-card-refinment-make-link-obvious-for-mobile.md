# Story 5-3: Company Card Refinement - Mobile Link Affordance

## Status
- **Status:** done
- **Priority:** Medium
- **Effort:** Small

## Story
**As a** Mobile User,
**I want** the company card to clearly indicate it is clickable,
**So that** I know I can view the detailed report.

## Context
On desktop, hover effects (background change, arrow translation) indicate interactivity. On mobile, these cues are missing. The gray arrow is too subtle. We need an explicit visual cue.

## Acceptance Criteria

### AC1: Visible CTA on Mobile
**Given** the company card is viewed on a mobile device (width < 640px),
**When** I look at the card,
**Then** I see a clear "View" or "Report" indicator, or the arrow is colored distinctly (Primary Color) to suggest a link.
- **Proposal**: Change arrow color to Primary and/or add "View" text label.

### AC2: Consistent Layout
**Given** the layout changes,
**When** I view on Desktop,
**Then** the hover effects still work and the layout remains clean.

## Technical Notes
- **Component**: `execution/frontend/src/components/ui/CompanyCard.tsx`
- **Styling**: Tailwind CSS (use `md:` prefixes or styled-jsx media queries).

## Tasks
- [x] **Frontend**
    - [x] Update Arrow icon color/style for mobile ("Scorecard" text + Primary Color).
    - [x] (Optional) Add text label if icon isn't enough (Implemented "Scorecard" text).
    - [x] Verify responsiveness (Hidden on desktop, visible on mobile).

## Dev Agent Record

### File List
- `execution/frontend/src/components/ui/CompanyCard.tsx` (Added responsive link affordance)

### Change Log
- **2026-02-06**: Implemented Mobile Link Affordance.
    - [x] AC1: Added "Scorecard" text and primary color styling for screens < 640px.
    - [x] AC2: Preserved clean desktop layout with hover effects.
