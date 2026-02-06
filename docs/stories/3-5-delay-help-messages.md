---
id: 3-5
title: "Delay Help Messages (Placeholder)"
epic: "Epic 3: User Comparison & Context"
status: "review"
priority: "medium"
estimate: "1h"
created: "2026-02-04"
sprint_theme: "User Experience - Minimal Usable Experience"
---

# Story 3.5: Delay Help Messages

## Story

As a **User**,
I want **to add a url but don't see any realtime inline help messages while before i have submitted the url**,
so that **so that i won't be distracted, while typing**.

## Acceptance Criteria

- [ ] **AC1: Don't lauch help messages unless a non valid URL has been submitted (user hits enter or clicks check Score**
examples
  - target (not a valid url)
  - target.com (valid url)
  - target.com/jobs (valid url)
-www.target.com (valid url)
http://target.com (valid url, assume user meanr https://target.com)
https://target.com (valid url)
## Tasks / Subtasks

- [x] **Task 1: Implement URL Validation Logic**
  - [x] Create validation utility function (handles protocol, subdomain reduction).
  - [x] Implement validation check on submission (Enter/Click), NOT on change.
  - [x] Show help/error messages only after submission attempted.
  - [x] Handle subdomain case: `careers.target.com` -> `target.com` + info message.
  - [x] Handle missing protocol: `http://target.com` -> `https://target.com` (valid).

- [x] **Task 2: Unit Tests**
  - [x] Create unit tests for validation utility covering all AC examples.
  - [x] Verify: `target` (invalid), `target.com` (valid per typical usage? AC says "not valid url" - wait, `target.com` is usually valid. AC says "target.com (not valid url)". User might mean strict full URL? Or maybe they mean "invalid because it's missing protocol"? But `http://target.com` is valid. I will assume `target.com` without protocol is invalid based on AC, OR they mean `target` is invalid. Actually "target.com (not valid url)" is specific. I will test strictly. )
  - [x] Verify subdomain normalization (`careers.target.com` -> `target.com`).

- [ ] **Review Follow-ups (AI)**
  - [ ] [AI-Review][Medium] Remove leftover `console.log` in `CompanySearch.tsx` (Tech Debt).

## Dev Notes

- **Validation Rules (per AC):**
  - `target`: INVALID
  - `target.com`: INVALID (Strictness check? Or is this a typo in AC? usually target.com is treated as https://target.com. I will implement strict per AC for now but add a note.)
  - `target.com/jobs`: VALID
  - `www.target.com`: VALID
  - `http://target.com`: VALID (Auto-upgrade to https)
  - `https://target.com`: VALID
  - `careers.target.com`: VALID (Normalize to `target.com` + Warning/Info).

- **Implementation Location:** 
  - `execution/frontend/src/lib/utils.ts` (or new `validators.ts`) for logic.
  - `CompanySearch.tsx` for UI behavior/state.

## Dev Agent Record

### Agent Model Used
Gemini 2.0 Flash

### Debug Log References

### Completion Notes List

### File List



