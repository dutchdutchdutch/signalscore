# SignalScore Methodology

**SignalScore** analyzes public signals to measure a company's AI readiness. It helps job seekers, investors, and employees identify "AI-forward" organizations versus those still operating on legacy patterns.

The goal is to provide transparency into which companies are actively building with modern AI tools versus those that may be falling behind in the agentic transformation. The system employs **autonomous discovery agents** to finding, scanning, and synthesizing signals from multiple verified sources.

## How Scoring Works

Companies are scored on a **0–100 scale**, derived from five key signal categories.

### 1. Signal Categories

| Category | Weight | Description |
|:---------|:-------|:------------|
| **AI Keywords** | 25% | Frequency of AI/ML terms (e.g., "machine learning", "LLM", "generative AI") across careers pages and blogs. |
| **Agentic Signals** | 20% | Evidence of autonomous systems (e.g., "orchestration", "self-healing", "agents"). This distinguishes modern AI engineering from traditional ML. |
| **Tool Stack** | 20% | Presence of known AI tools (PyTorch, SageMaker, LangChain, Vercel AI SDK, etc.) in job descriptions and tech blogs. |
| **Non-Eng AI Roles** | 25% | AI adoption in non-engineering functions (Marketing, HR, Finance). This indicates organizational buy-in beyond just R&D. |
| **AI Platform Team** | 10% | Existence of a dedicated AI/ML infrastructure or platform team, suggesting mature operational capabilities. |

### 2. Source Reliability

Not all signals are equal. We weight evidence based on the verifiability of the source to prevent "AI-washing".

-   **High Confidence (2.0x)**: GitHub activity, Open Source contributions, detailed Job Descriptions (ATS-integrated), dedicated AI subdomains (`ai.company.com`).
-   **Medium Confidence (1.5x)**: Engineering Blogs with technical depth.
-   **Low Confidence (0.5x)**: Marketing homepages and press releases.

### 3. The Score

The final score represents a company's maturity level:

-   **95–100 (Transformational)**: Industry-defining AI adoption.
-   **80–94 (Leading)**: Strong public AI signals, dedicated teams, modern tooling.
-   **60–79 (On Par)**: Operational AI presence, actively hiring for AI roles.
-   **30–59 (Trailing)**: Limited AI signals, early exploration phase.
-   **0–29 (Lagging)**: Minimal or no public AI activity.

---

*This methodology is open source and evolving. Contributions and feedback are welcome on [GitHub](https://github.com/dutchdutchdutch/signalscore).*
