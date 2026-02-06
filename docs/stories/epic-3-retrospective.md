# Epic 3 Retrospective: User Comparison & Context

Status: done

## Story

As the **Development Team**,
I want to **conduct a retrospective for Epic 3**,
so that **we can improve our velocity, code quality, and testing processes for Epic 4.**

## Acceptance Criteria

1.  **AC1: Metrics Analysis**
    -   Calculate total story points verified vs. planned.
    -   Identify cycle time bottlenecks (e.g., test environment issues).

2.  **AC2: "What Went Well"**
    -   Document successful features (Processing Experience, Visual Refresh).
    -   Highlight effective workflows (e.g., polling logic).

3.  **AC3: "Improvements Needed"**
    -   Address the persistent `EPERM` test environment issue.
    -   Address scraping reliability or mocking strategies.

4.  **AC4: Action Plan**
    -   Create concrete action items for Epic 4 startup.
    -   Update `sprint-status.yaml` if necessary.

## Tasks / Subtasks

-   [ ] **Task 1: Analyze Sprint Metrics**
    -   [ ] Review completed stories (3.1 - 3.7).
    -   [ ] Calculate velocity.

-   [ ] **Task 2: Document Learnings**
    -   [ ] Write "Start/Stop/Continue" analysis.
    -   [ ] Specifically investigate the `EPERM` issue root cause (or plan to).

-   [ ] **Task 3: Plan Epic 4**
    -   [ ] Review backlog for Epic 4.
    -   [ ] Validate priorities.

## Dev Notes

-   **Context:**
    -   Story 3.3 faced significant local testing issues (`EPERM`).
    -   Story 3.1 and 3.4 went smoothly.
    -   Scraping reliability is a known backlog item (4.4).

## Retrospective Analysis

### Metrics
- **Planned Stories:** 7 (3.1 - 3.7)
- **Completed Stories:** 7
- **Velocity:** High (Estimated ~15h total work delivered).
- **Process Gap:** Stories 3.4, 3.6, and 3.7 were implemented and marked done in `sprint-status.yaml` but their individual story files still show `ready-for-dev` or `review`.
  - *Action:* Ensure `update-story-status` is part of the definition of done.

### What Went Well ("Green")
- **"System Minimal" Design:** The new visual direction (Story 3.1) was implemented smoothly and looks great.
- **Polling Logic:** The `ProcessingState` (Story 3.3) implementation with polling was robust.
- **Velocity:** The team moved through 7 stories quickly, including a complex detail page and bug fixes.

### Improvements Needed ("Red")
- **Test Environment (Critical):** `npm run test` consistently fails with `EPERM` errors on the local environment for watching/checking files.
  - *Impact:* Relied on manual verification for Story 3.3.
  - *Fix:* Investigate Vitest watcher permissions or Dockerize the test runner.
- **Documentation Hygiene:** As noted in metrics, story file status became de-coupled from sprint status.

### Investigation: EPERM Error
- **Issue:** `Error: EPERM: operation not permitted, mkdir '/var/folders/.../client'` during Vitest execution.
- **Analysis:** Likely related to MacOS sandbox permissions or Vitest's cache mechanism trying to write to a protected temp directory.
- **Mitigation:** Used `--no-cache` which helped partially but didn't solve the watcher issue.

## Action Plan for Epic 4

1.  **Fix Test Runner:** Priority #1 before deep work on Epic 4.
2.  **Epic 4 Kickoff:**
    -   Focus: Admin Operations & "Self-Annealing" (improving data quality).
    -   Key Story: `4-2-research-thoroughness` (addressing user feedback on shallow validation).
3.  **Process:** strict adherence to updating story file status.

## Dev Agent Record

### Agent Model Used

Antigravity (Gemini 2.0 Flash)

### Completion Notes List

- Verified all Epic 3 stories.
- Confirmed discrepancies in story metadata vs code state.
- Documented testing blockers.
- Outlined Epic 4 focus.

### File List
- docs/stories/epic-3-retrospective.md
- docs/stories/sprint-status.yaml

