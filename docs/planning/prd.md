---
stepsCompleted:
- step-01-init
- step-02-discovery
- step-03-success
- step-04-journeys
- step-05-domain
- step-06-innovation
- step-07-project-type
- step-08-scoping
- step-09-functional
- step-10-nonfunctional
- step-11-polish
inputDocuments:
- product-brief-signalscore-2026-02-03.md
documentCounts:
  briefCount: 1
  researchCount: 0
  brainstormingCount: 0
  projectDocsCount: 0
classification:
  projectType: web_app
  domain: general
  complexity: medium
  projectContext: greenfield
workflowType: 'prd'
---

# Product Requirements Document - SignalScore

**Author:** User
**Date:** 2026-02-03

## Executive Summary
**Vision:** SignalScore is the "Glassdoor for AI Readiness." It helps job seekers avoid career stagnation by surfacing which companies are truly building the future (AI-Native/Forward) versus those stuck in the past (Legacy/Lagging).

**Core Differentiator:** While LinkedIn shows *who* works there, SignalScore reveals *what* they are actually building by analyzing public signals (Engineering Blogs, Job Descriptions, 10-K Filings) to generate a trusted "AI Readiness Score."

---

## Success Criteria

### User Success
*   **Decision Conversion Rate**: >15% of searches lead to a measurable "Negative" decision (avoidance value), helping users dodge legacy roles.
*   **Research Time Compression**: Collapse 8-15 hours of manual research into <30 minutes of tool usage.
*   **Avoidance Value**: Users successfully identify and avoid "Legacy Trap" roles that would have stalled their career growth (measured by user stories/feedback).

### Business Success
*   **Prediction Accuracy**: High correlation between our "AI Readiness Score" and post-hire reality (validated via 3/6/12 month cohort analysis).
*   **Signal Quality**: >40% verification rate on collected data points.
*   **Engagement**: Users comparing 3+ companies in single sessions (indicating deep evaluation).

---

## Innovation & Novel Patterns

### Detected Innovation Areas
*   **"Mismatch as Validity" Protocol**: Unlike traditional scrapers that fail on missing data, SignalScore treats "missing public signal" as a data point in itself. If a company claims to be AI-forward but has zero public footprint, that "Noise" becomes a "Signal" of poor recruitment hygiene.
*   **Career Risk Hedging Framework**: Reframes job hunting from "Finding Opportunity" to "Managing Obsolescence Risk." This psychological shift is a novel market entry point compared to LinkedIn/Glassdoor.
*   **Self-Annealing Scraper Ops**: The Admin workflow is designed not to "fix data" but to "teach patterns" (e.g. adding a Notion page structure as a valid career site), creating a system that gets smarter with every edge case.

### Validation Approach
*   **Retrospective Backtesting**: Validate the "Risk Score" by running it against companies that *failed* or laid off staff in 2023/24. Did they have a "Lagging" score 12 months prior?
*   **User "Aha!" Tracking**: Measure how often users click "How is this calculated?" immediately after seeing a "Lagging" score for a big-name company. This validates the "Reality Check" value.

---

## User Journeys

### Elena (Job Seeker) - The "Dodged Bullet"
*   **Trigger**: Elena sees a "Senior Product Manager" role at *LegacyCorp* with a 20% pay bump. The sheer salary is tempting.
*   **Action**: Before applying, she navigates to SignalScore and pastes the *LegacyCorp* URL.
*   **System Response**: Returns "Score: 1/5 - Lagging".
*   **Discovery**: She reviews the evidence: "0% of Engineering roles mention 'Agents' or 'LLM' in last 12 months", "CTO's last public talk was on 'Cloud Migration' in 2022".
*   **Outcome**: She realizes the role will be maintaining legacy systems, not building the future. She perceives the high salary as "danger pay." She abandons the application and focuses her energy on a "Fast Follower" company offering less cash but more skills growth.
*   **Emotional State**: Relief. She feels she just saved herself 2 years of stagnation.

### Marcus (VP Engineering) - The "Reality Check"
*   **Trigger**: His CEO asks, "Are we falling behind on AI? The board is asking."
*   **Action**: Marcus checks his own company on SignalScore.
*   **System Response**: Returns "Score: 2/5 - Trailing".
*   **Discovery**: He feels a pang of defensiveness, but then clicks "How is this calculated?". He spots the gap: "No public engineering blog posts on AI." He realizes his team *is* doing the work, but not signaling it.
*   **Outcome**: He copies the "Missing Signals" list and sends it to his DevRel team: "We need to publish our agent work this month to fix our recruitment signal."
*   **Value**: SignalScore becomes his external audit tool.

### Admin (System Operator) - The "Algorithm Tuner"
*   **Trigger**: System flags *NewStartup.io* with "Low Confidence Score (30%)" because the scraper failed to find a traditional "Careers" page (they use a bespoke Notion site).
*   **Action**: Admin investigates the failure. Instead of manually fixing the data for just this one company, the Admin adds *NewStartup.io* as a test case in the "Scraper Training Set."
*   **System Response**: The admin tags the Notion URL structure as a valid "Careers Page Pattern."
*   **Outcome**: The system re-runs the "Site Discovery" algorithm. It successfully ingests *NewStartup.io* AND 50 other startups using similar Notion templates, auto-correcting their scores from "Unknown" to "Walking/Running."
*   **Value**: Sustainable scaling. One fix solves 50 future problems.

---

## Functional Requirements

### Search & Discovery
*   **FR01**: User can search for a company by Name or URL, receiving instant feedback if the company is indexed or not.
*   **FR02**: User can view a company's "AI Readiness Score" (1-5 Level) clearly displayed on the profile.
*   **FR03**: User can view the detailed "Evidence List" justifying the score, including specific positive/negative signals found.
*   **FR04**: User can see the "Confidence Level" (High/Medium/Low) of the score based on data density/quality.
*   **FR05**: User can submit a request to "Add a Company" if it is missing from the index, which queues it for the scraping pipeline (Phase 1b).
*   **FR06**: User can switch between "Job Seeker" view (Risk focus) and "Benchmarker" view (Comparison focus).

### Scoring Engine & Backend
*   **FR07**: System can ingest and parse content from public URLs (Careers Pages, Engineering Blogs, 10-K Filings, Press Releases).
*   **FR08**: System can vary scraping strategy based on site type (e.g. Greenhouse embedding vs standard HTML).
*   **FR09**: System can identify and classify specific "AI Roles" (e.g. LLM Engineer, Agent Orchestrator) vs "Legacy Roles" using keyword/semantic matching.
*   **FR10**: System can extract and validate "Public Activity" timestamps (e.g. Last tech blog post date) to ensure freshness.
*   **FR11**: System allows "Missing Data" (e.g. no blog found) to be weighed as a negative signal in the scoring algorithm.
*   **FR12**: System automatically expires/invalidates signals older than 12 months.

### Admin & Operations
*   **FR13**: Admin can manually override a calculated score and attach a "Correction Reason" for audit trails.
*   **FR14**: Admin can view "Scraper Failures" and manually map URL patterns to fix extraction issues (Self-Annealing).
*   **FR15**: Admin can trigger a manual "Re-Score" for a specific company to force an update.
*   **FR16**: Admin can upload "Ground Truth" datasets to validate scoring accuracy against reference companies.

---

## Non-Functional Requirements

### Performance & Reliability
*   **Time to Interactive**: <1.5s (Core Web Vitals "Good" threshold) on Company Profile pages.
*   **Score Latency**: Cached scores must load in <200ms.
*   **Scraper Success Rate**: >80% of "Top 50" careers pages must be scrapable without human intervention.
*   **Freshness**: All scores are re-calculated automatically every 30 days.

### Security, Compliance & Ethics
*   **Rate Limiting**: Public API/Search limited to 10 requests/minute per IP.
*   **Polite Scraping**: Scrapers must respect `robots.txt` and implement aggressive caching (min 24h).
*   **Data Rights**: Analysis strictly limited to publicly available URLs. No "leaked" data.
*   **Disclaimer**: Distinct "For Informational Purposes Only" disclaimer visible on all scores.

### SEO (Web App Specific)
*   **Sitemap**: Auto-generated `sitemap.xml` for all "Scored Companies" must update within 24h of ingestion.
*   **Metadata**: Dynamic OpenGraph images for social sharing (e.g. "Stripe - AI Readiness: 5/5").

---

## Technical Stack & Architecture

*   **Backend (The Intelligence)**: Python.
    *   **Libraries**: BeautifulSoup/Playwright (Scraping), Pandas/Numpy (Data), LangChain (AI).
    *   **Role**: Handling all scraping, scoring, vector embeddings, and API service.
*   **Frontend (The Face)**: Next.js.
    *   **Role**: Best-in-class SEO (Server-Side Rendering), fast performance for directory pages.
*   **Database**: SQLite (MVP).
    *   **Role**: Zero-config, portable file-based DB for initial validation. Path to Postgres migration.
*   **Hosting**: Google Firebase (Free Tier).

---

## Project Scoping & Phased Development

### MVP Strategy (Phase 1a - "Walking Skeleton")
**Goal**: User validation of the *Rubric*, not the *Database*.
**Target**: 5-10 "Reference Companies" (Mix of known Leaders/Laggards).
*   **Constraint**: If our tool doesn't yield a DIFFERENT decision than a Google Search in 30 seconds (Insight Delta), we fail.
*   **Feature Set**: End-to-End Scraper → Scorer → Frontend pipeline. Manual "Ground Truth" override.

### Phase 1b (Scaling)
**Target**: Top 50 AI Forward + 50 Legacy Control Group.
*   **Goal**: Validate the algorithm's ability to self-sort companies without manual help.
*   **Feature**: "Submit a Company" button for users to queue new additions.

### Future Vision (Phase 2+)
*   **Personalized Career Pathing**: Matching resumes to "Leading" companies.
*   **B2B Audits**: "Improve your Score" services for companies.
*   **Market Standard**: Becoming the de-facto score for company tech health.
