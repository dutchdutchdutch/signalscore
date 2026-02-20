# SignalScore: Auditing AI Readiness

## WHAT is SignalScore?  

SignalScore is an open-source intelligence engine that quantifies a company’s actual AI adoption and benchmarks its AI readiness. SignalScore is an [active research project](#development-notice-and-forward-looking-information).

SignalScore **measures what companies *do*, not what they *claim***. The system scrapes verifiable external signals: job postings, GitHub contributions  showing agentic orchestration, engineering blogs detailing production LLM infrastructure. Early research shows AI expectations in non-engineering job postings correlate most strongly with genuine transformation.

## WHY SignalScore?  
The next 18–24 months will be defined by Agentic Augmentation, where autonomous systems perform common tasks and enable higher-quality human decisions. **To navigate the Agentic Shift**, leaders need a dual-lens approach. Legacy frameworks remain necessary for auditing *safety* (Infrastructure, Security, Governance). New Dynamic frameworks, like SignalScore to measure operational throughput. 

Legacy assessment frameworks rely on self-reporting  that mostly capture Internal Intent". Predictable result: overestimation. When 75% of knowledge workers use ChatGPT for commodity tasks, internal surveys report "widespread AI adoption" while teams still manually review most outputs, go to the same amount of status meetings, and collaborate per legacy norms, negating automation ROI.

The measurement gap creates strategic blind spots:

* Organizations believe their "AI upskilling mandate" succeeded while many employees see it as extra work  
* Boards approve AI budgets based on inflated capability assessments  
* Leadership mistakes tool deployment for workflow transformation

Companies integrating agentic workflows compress quarterly timelines into weeks. S\&P 500 firms with productivity AI adoption show 29% faster stock price growth than the broader market. Misreading your position is an existential threat.

Direct research prompts surface insights, but without benchmarks you're navigating blind. That's exactly why SignalScore exists.


## WHO Benefits from SingleScore?    
SignalScore separates leaders from laggards in AI Readiness \- **providing decision intelligence for:**

* **Executives:** Audit organizational AI readiness without internal self-assessment bias. Public signals expose gaps between strategy and execution.  
* **Investors:** Validate AI adoption claims during due diligence. A company claiming "AI-powered" with a dated tech stack or zero AI platform engineers is a significant red flag.  
* **Job-Seekers & Employees:** Evaluate if a company's "AI transformation" is real. Job seekers can assess whether a role is forward-looking or AI-vulnerable, while current employees can benchmark their employer against competitors to assess career risk.

The stakes: Organizations scoring above 80 (Leading) achieve 2.8x faster product release cycles. Employees at firms scoring  below 60 (Trailing) face 18-24 month skill obsolescence and 29% wage penalties. SignalScore provides the data to choose acceleration over stagnation.

## HOW  SingleScore measures  AI Readiness measured

The SignalScore architecture operates on the premise that genuine technological shifts leave a digital trail. The model uses autonomous discovery agents to crawl public digital artifacts, aggregating data across five weighted categories to calculate a "Kinetic Energy" score. Results are normalized against a "Ground Truth" dataset of verified AI-forward firms (e.g., Google, Shopify).

### The Five Core Signals (0–100 Rating):

1. **AI Keywords (25%):** Uses a three-tier scoring system that separates signal from noise. **Success Evidence** (3 pts per match) captures proof of AI in production — deployed models, inference pipelines, measurable ROI. **Strategy/Plan** (2 pts) captures roadmap signals — AI-first mandates, Chief AI Officer hires, dedicated budgets. **Generic Mentions** (1 pt) captures baseline references — "machine learning," "data science," "LLM." This tiered approach rewards companies showing results over those only talking about plans.
2. **Agentic Signals (20%):** The most forward-looking metric, hunting for the vocabulary of the *next* phase of AI: "Orchestration," "Self-healing," "Multi-agent workflows," and emerging indicators like "Model Context Protocol," "LLM-ready documentation," and "AI-friendly documentation." This detects movement toward Agentic flows and AI-optimized infrastructure.
3. **Non-Engineering Roles (25%):** A critical differentiator, scanning for AI adoption in departments like Finance, HR, Marketing, Legal, Sales, and Operations. High scores here indicate Systemic adoption (Gartner Level 4), not isolated R\&D. Scores are boosted when non-engineering job descriptions contain agentic keywords (agent, orchestration, automation, GenAI), with additional weight for Director and Lead-level roles — signaling executive commitment to AI-augmented workflows.
4. **Tool Stack (20%):** Identifies the "Tools of the Trade" using source-weighted detection. Tools found in GitHub repos or verified job postings carry higher weight than homepage mentions. Tracked tools include frameworks (PyTorch, TensorFlow), LLM tooling (LangChain, OpenAI, Anthropic, Hugging Face), cloud platforms (AWS, GCP, Azure, Databricks), and AI-native dev tools (Copilot, Cursor, Replit).
5. **AI in IT (10%):** Measures AI keyword density within engineering-specific sources (GitHub, engineering blogs, verified job postings). Detection of a dedicated AI platform team acts as a score floor, confirming the company is building the infrastructure layer required for agents to function on internal data.

#### Verification, Bonuses, and Penalties
To mitigate "AI-washing" risk, each source type carries a credibility multiplier:

| Source Type | Weight | Rationale |
| ----- | ----- | ----- |
| GitHub / Verified Job Posting / ATS Link | **2.0x** | Hard evidence of implementation or hiring intent |
| Engineering Blog / Careers Page | **1.5x** | Technical depth, active recruiting |
| Investor Relations | **1.0x** | Public commitments with accountability |
| News / Press Release | **0.75x** | Third-party coverage, subject to recency decay |
| Homepage | **0.5x** | Marketing copy, lowest credibility |

**Recency Weighting:** News and press sources are subject to date-based decay — full weight within 45 days, half weight at 45–90 days, zero weight beyond 90 days.

**Excellence Boost:** A **\+10 Bonus** is awarded if two or more categories score above 90, rewarding companies with exceptional depth across multiple signals.

**High-Water Mark ("3 of 5 Rule"):** If three or more categories score above 80, the company is guaranteed at least an "On Par" rating — preventing strong multi-signal profiles from being dragged down by one weak area.

**Marketing-Only Penalty:** If AI keywords appear exclusively on the homepage with zero corroboration from engineering sources (GitHub, blogs, job postings) or investor relations, keyword, tool stack, and AI-in-IT scores are reduced by 50%.

### SignalScore Readiness Tiers

| Score Range | Category | What It Means |
| ----- | ----- | ----- |
| **95–100** | **Transformational** | Industry-defining AI adoption; agentic workflows in production, AI embedded widely across non-engineering functions. |
| **80–94** | **Leading** | Strong public signals; dedicated AI platform teams, modern tooling, and AI adoption in non-engineering functions. |
| **60–79** | **On Par** | Operational AI presence; actively hiring AI roles, some tool adoption, limited agentic signals. |
| **30–59** | **Trailing** | Early exploration; AI keywords in job posts, but no platform team or systematic deployment. |
| **0–29** | **Lagging** | Minimal public AI activity; homepage mentions AI, but zero engineering evidence. |

**Limitations**

* **Public Signal Dependency:** Private companies with closed GitHub repos may score lower than justified.  
* **Industry Variance:** Regulated sectors (finance, healthcare) with limited public disclosure can create false negatives.  
* **Time Lag:** Structural changes may manifest 6–12 months before being reflected in public signals.  
* *Note: SignalScore allows for direct URL submission to rescore a company.*

## HOW Does SignalScore compare?  

| Framework | What it Evaluates | Assessment Type | Accessibility from Outside |
| ----- | ----- | ----- | ----- |
| **Cisco AI Readiness Index** | 6 pillars: Strategy, Infrastructure, Data, Governance, Talent, Culture. | Self-Evaluation (Survey-based). | Highly Accessible; free online diagnostic tool. |
| **Microsoft AI Assessment** | 5 drivers of value (Strategy, Culture, Governance) & Cloud Adoption stages. | Self-Evaluation (Wizard) / Hybrid implementation. | Highly Accessible (Wizard); Technical documentation is public. |
| **Deloitte AI Maturity Models** | Strategy, Data, Tech, Culture, Outcomes, and Applied Trust. | Consultant Assessment (High-touch). | Limited; requires engagement. |
| **Gartner AI Maturity Model** | 5 levels of development across 7 organizational pillars. | Analyst Assessment / Subscriber Toolkit. | Low; restricted to Gartner clients. |
| **SignalScore** | 5 weighted public signals: AI Keywords (tiered), Agentic Signals, Tool Stack (source-weighted), Non-Eng Roles, AI in IT. | Automated External Scraping (Objective/Hard Evidence). | Instant; Open Source web app. |

### DO The Dual Mandate: Defense and Offense

The established consulting frameworks are designed to measure compliance and foundation. SignalScore is the survival tool designed to measure *speed*. You must actively track the **"Kinetic Energy"** of your AI adoption to avoid being rendered obsolete.

1. **Use Big Firm Models (Cisco/Gartner) for Defense:** Ensure your foundation (Infrastructure, Security, Governance) is compliant and scalable.  
2. **Use SignalScore for Offense:** Audit your *actual* market posture. Run it against your own public footprint.  
3. **Self-Correct:** If your internal Gartner assessment says you are "Level 4 (Systemic)" but your SignalScore is "35 (Trailing)," you have a **"Marketing-Reality Gap"** ;you are likely talking about AI more than you are leveraging it.*

## Act Now

* **[Score Your Company](https://signalscore-app.com)**
* **[Connect with SignalScore](mailto:dutch@signalscore.com)** Inquire about domain customizations.
---
#### Development Notice and Forward Looking Information
 SignalScore is an active research project. Scoring methodology, benchmark correlations, and performance predictions described here represent current implementation and preliminary findings, subject to revision as validation data expands. Scores reflect publicly observable signals only—not comprehensive internal capabilities. Not investment, employment, or strategic advice. Conduct independent research before making decisions. See github.com/dutchdutchdutch/signalscore for current limitations.

*Contributions and feedback are welcome on [GitHub](https://github.com/dutchdutchdutch/signalscore).*
