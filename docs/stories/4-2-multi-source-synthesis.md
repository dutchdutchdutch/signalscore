# Story 4.2: Multi-Source Synthesis

Status: ready-for-dev

## Story

As a **User**,
I want the system to **intelligently aggregate signals from multiple sources (HomePage, Blog, GitHub, Job Board)**,
so that the final AI Readiness Score reflects a **holistic view of the company**, handling conflicts (e.g., Marketing says "AI First", GitHub says "No Code") appropriately.

## Context

In Story 4.1, we implemented the "Deep Discovery" agent which now finds and scrapes satellite sources. Currently, the scoring logic treats these sources somewhat independently or just adds them to the mix. We need a robust synthesis layer that weighs different sources based on their reliability for specific signals (e.g., GitHub is better for "Tool Stack" than a Press Release).

## Acceptance Criteria

1.  **AC1: Weighted Signal Aggregation**
    -   Define reliability weights for different source types per component:
        -   **Tool Stack:** GitHub (High), Engineering Blog (Medium), Homepage (Low). AI/ML engineering roles listing ai related tool stack
        -   **AI Strategy:** Investor Relations/Press (High), Homepage, working at, about us, press releases (Medium). AI/ML company listing ai strategy
        -   **Agentic Usage within engineering:** Job Descriptions (High), Engineering Blog (High). AI/ML engineering roles listing ai related tool stack
        -  **Agentic Usage outside of engineering:** Job description for middle management roles like product, marketing and legal Lead and director roles (very high), conference and speaking engagements about this topic (High).
    -   Algorithm should prioritize high-confidence sources when signals conflict.

2.  **AC2: Source Attribution**
    -   The UI should clearly indicate *which* source contributed to *which* signal.
    -   Example: "Tool Stack: LangChain (Found in GitHub)", "Role: AI Product Manager (Found in Careers Page)".

3.  **AC3: Conflict Resolution**
    -   If Homepage says "We use AI" but public Github contributions shows 0 AI activity/repos, lower the "Implementation" score or flag as "Marketing Only". it is likely an AI consumer of generic platforms. 
    -   (MVP: Simple weighted average or priority override is fine).

4.  **AC4: Confidence Score Refinement**
    -   Update the existing "Confidence Score" logic to explicitly factor in *number of distinct sources* verified.
    -   1 source (Homepage only) = Low Confidence.
    -   3+ sources (Homepage + GitHub + Blog) = High Confidence.

## Tasks / Subtasks

-   [ ] **Task 1: Scoring Algorithm Update (`ScoringService`)**
    -   [ ] Implement weighted aggregation logic.
    -   [ ] Add reasoning/citations to the score output (linking signals to specific source URLs).

-   [ ] **Task 2: UI Updates (`SignalDetailPage`)**
    -   [ ] enhance "Deep Research Sources" to show what signals were extracted from each.
    -   [ ] (Optional) Visual indicator of source contribution in the main score card.

-   [ ] **Task 3: Verification**
    -   [ ] Unit tests for aggregation logic (mocking conflicting inputs).
    -   [ ] E2E test on a company with known conflicting signals (or a diverse footprint).

## Dev Notes

-   **Data Structure:**
    -   We likely need to restructure `SignalData` to carry metadata about *where* a keyword was found, not just the count.
    -   Current: `tools_found: ["PyTorch"]`
    -   Target: `tools_found: [{ name: "PyTorch", source: "github_repo_1" }]`
