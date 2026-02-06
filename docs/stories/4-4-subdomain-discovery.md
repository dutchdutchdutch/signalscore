# Story 4.4: Subdomain & Product Ecosystem Discovery

## Status
- **Status:** done
- **Priority:** High
- **Effort:** Medium

## Story
**As a** Score Consumer,
**I want** the system to discover and analyze relevant subdomains (e.g., ai.google.com, research.facebook.com, developer.netflix.com),
**So that** large technology companies receive credit for their dedicated AI/Engineering portals, even if the main `.com` marketing site is generic.

## Context
Feedback from Story 4.3 revealed that while we can now find Job Descriptions, we still miss the massive AI footprint of tech giants because it lives on dedicated subdomains (specifically `gemini.google.com`, `firebase.google.com`, `ai.google`). A generic "Subdomain Scanner" is needed to check for high-signal prefixes.

## Acceptance Criteria
1.  **AC1: Generic Subdomain Scanning**
    - The `DiscoveryService` must systematically check for high-value subdomains: `ai`, `research`, `labs`, `engineering`, `developers`, `tech`, `blog`, `cloud`.
    - It should verify these exist (HTTP 200) before adding them to the scrape list.

2.  **AC2: Weighted Scoring for Ecosystem**
    - Signals found on `ai.*` or `research.*` should carry **High Weight (1.5 - 2.0)**.
    - Finding a valid `ai.` subdomain itself is a positive signal (AI Presence).

3.  **AC3: Google Benchmark**
    - Re-running the evaluation on Google should yield a score > 40.0 by successfully ingesting content from `ai.google` or similar detected subdomains.

## Technical Approach
- **Service:** `DiscoveryService.discover_subdomains(domain)`
- **Heuristic:** requests to `https://{prefix}.{domain}` with a timeout.
- **Scoring:** Update `calculator.py` to recognize `subdomain_ai` or `subdomain_research` source types.

## Tasks
- [ ] **Discovery Update**
    - [ ] Implement `SubdomainScanner` in `DiscoveryService`.
    - [ ] Add list of "High Signal Prefixes" (`ai`, `research`, `labs`, `dev`).
- [ ] **Scoring Update**
    - [ ] Update `ScoringService` to scrape discovered subdomains.
    - [ ] Update weights: `subdomain_ai` = 2.0, `subdomain_dev` = 1.5.
- [ ] **Verification**
    - [ ] Verify Google score improvement.
