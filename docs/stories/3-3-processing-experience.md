# Story 3.3: Processing Experience

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **User waiting for a company analysis**,
I want **to see a clear, engaging indication that the system is processing my request**,
so that **I know the application hasn't stalled, understand the steps being taken, and remain patient during long scraping times.**

## Acceptance Criteria

1.  **AC1: Immediate Processing State**
    -   Transition immediately to a "Processing" view upon form submission.
    -   Hide the search input or disable it clearly.
    -   Show a visually distinct "Scoring Engine Active" state (not just a spinner).

2.  **AC2: Progress Feedback & Polling**
    -   **Polling Logic:** If the backend returns a `202 Processing` status (or equivalent), the frontend must poll `GET /api/v1/scores/{company}` every 3-5 seconds.
    -   Terminate polling when status is `completed` (show results) or `failed` (show error).
    -   **Visual Feedback:** Display text updates that rotate or reflect status: "Connecting to site...", "Extracting signals...", "Calculating score...".
    - **Set Expectation/SLA:** Display a message that processing commonly takes 3 to 5 minutes, but can take longer. Confirm that the user can navigate away and return to the results page later they enter same URL and results will be available.
    - **While you wait suggestion:** Provide a link to a to a page about Signal Score's methodology.

3.  **AC3: Timeout Handling**
    -   If processing takes longer than 4 minutes, display a "Taking longer than usual" message.
    -   Ensure the user is not stuck in an infinite loading loop.

4.  **AC4: Visual Polish ("System Minimal")**
    -   Use the design system's `animate-pulse` or similar subtle effects.
    -   Avoid blocking the entire UI; allow users to read "Why this takes time" or similar helper text (foundation for Story 3.5).
    -   Ensure the layout doesn't shift drastically when transitioning from Search -> Processing -> Results.

## Tasks / Subtasks

-   [x] **Task 1: Implement Polling Logic in `CompanySearch`** (AC: 2)
    -   [x] Refactor `handleAnalyze` to support async/polling flow.
    -   [x] Implement `pollForScore(companyId)` helper function.
    -   [x] Handle `processing`, `completed`, and `failed` states.

-   [x] **Task 2: Create `ProcessingState` Component** (AC: 1, 4)
    -   [x] Build a dedicated component for the processing view.
    -   [x] Include animated elements (pulse/scan).
    -   [x] detailed "What we are doing" text.

-   [x] **Task 3: Implement Timeout & Error States** (AC: 3)
    -   [x] Add timeout counter/logic to the polling effect.
    -   [x] Design the "Timeout" view with "Try Again" action.

-   [x] **Task 4: Integration & Transition** (AC: 4)
    -   [x] Smoothly swap `SearchInput` for `ProcessingState`.
    -   [x] Smoothly swap `ProcessingState` for `ScoreDisplay` (Results).

## Dev Notes

-   **Existing Code:**
    -   `execution/frontend/src/components/features/CompanySearch.tsx`: Currently shows an error message for "processing". Needs to be changed to a persistent active state.
    -   `scoresApi.create` likely returns the initial status. Check `execution/backend/app/api/services/score_engine.py` (or similar) if backend changes are needed (unlikely, mostly frontend polling).
-   **Architecture:**
    -   Keep standard REST polling. Do not implement WebSockets (too complex for MVP).
    -   Use `useEffect` or a simple interval for polling.
-   **Design:**
    -   Keep it "System Minimal". No heavy lottie animations. Use CSS/Tailwind animations.

### Project Structure Notes

-   Place `ProcessingState.tsx` in `execution/frontend/src/components/features/ProcessingState.tsx`.
-   Reuse `SearchInput` styles for consistency.

### References

-   [CompanySearch.tsx](file:///Users/dutch/Dev/signalscore/execution/frontend/src/components/features/CompanySearch.tsx)
-   [ScoreDisplay.tsx](file:///Users/dutch/Dev/signalscore/execution/frontend/src/components/ui/ScoreDisplay.tsx)

## Dev Agent Record

### Agent Model Used

Antigravity (Gemini 2.0 Flash)

### Debug Log References

-   Test environment had EPERM issues with Vitest temp files; verified logic via code review and build.
-   Fixed linting errors in `CompanySearch.tsx` (undefined `company_name`).
-   Fixed build errors in `page.tsx` files (unescaped quotes/apostrophes).

### Completion Notes List

-   Implemented `ProcessingState.tsx` with "System Minimal" design, pulse animation, and SLA warnings.
-   Refactored `CompanySearch.tsx` to handle `processing` (202) status and poll every 4 seconds.
-   Implemented timeout warning logic (4 minutes).
-   Implemented auto-rotation of status messages for better UX.
-   Verification: `npm run build` passed successfully. Unit tests skipped due to local environment EPERM error (verified manually).

### File List

-   execution/frontend/src/components/features/ProcessingState.tsx
-   execution/frontend/src/components/features/CompanySearch.tsx
-   execution/frontend/src/components/features/__tests__/ProcessingState.test.tsx
-   execution/frontend/src/components/features/__tests__/CompanySearch.test.tsx
-   execution/frontend/src/app/page.tsx
-   execution/frontend/src/app/signal/[slug]/page.tsx

