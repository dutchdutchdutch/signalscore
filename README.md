# SignalScore

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Next.js](https://img.shields.io/badge/Next.js-14+-black.svg)](https://nextjs.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)


SignalScore analyzes public signals to measure a company's AI readiness. 

 A streamlined intelligence tool that empowers employee, investors and job-seekers to instantly evaluate a company's true trajectory in the AI era. In a landscape where AI adoption forces rapid role evolution, employees currently lack reliable metrics to judge whether a company is accelerating or stagnating.

## Overview

The system scrapes publicly available data—careers pages, engineering blogs, GitHub profiles—and extracts signals related to AI/ML adoption. These signals are scored across multiple categories and aggregated into an overall "AI Readiness Score."

The goal is to provide transparency into which companies are actively building with modern AI tools versus those that may be falling behind in the agentic transformation. The system employs **autonomous discovery agents** to finding, scanning, and synthesizing signals from multiple verified sources, not just the homepage.

The [Methodology Article](docs/articles/scoring-methodology.md) provides more details about the WHAT, WHY, and HOW.

## Architecture

The project follows a decoupled full-stack architecture:

- **Frontend**: Next.js (App Router) for SEO-optimized company profiles
- **Backend**: Python/FastAPI for scraping, scoring logic, and API services
- **Database**: SQLite (MVP) with path to Postgres

See the [C4 Diagrams](.agent/context/) for detailed architecture views:
- [System Context](.agent/context/c4_context.mmd) - External actors and system boundaries
- [Container Diagram](.agent/context/c4_container.mmd) - Applications and data stores
- [Component Diagram](.agent/context/c4_code.mmd) - Backend service internals
- [**Scoring Flow**](.agent/context/scoring_sequence.mmd) - Step-by-step sequence of discovery, scraping, and calculation

## How Scoring Works

### Signal Categories

Companies are analyzed across five weighted signal categories:

| Category | Weight | Description |
|:---------|:-------|:------------|
| **AI Keywords** | 25% | Frequency of AI/ML terms (e.g., "machine learning", "LLM", "generative AI") |
| **Agentic Signals** | 20% | Evidence of autonomous systems (e.g., "orchestration", "self-healing", "agents") |
| **Tool Stack** | 20% | Presence of known AI tools (PyTorch, SageMaker, LangChain, etc.) |
| **Non-Eng AI Roles** | 25% | AI adoption in non-engineering functions (Marketing, HR, Finance) |
| **AI Platform Team** | 10% | Dedicated AI/ML infrastructure or platform team |

### Verification & Benchmarking

To ensure scoring accuracy, the system is validated against a **Ground Truth** dataset of verified companies (e.g., Stripe, Dropbox).

*   **Benchmark Script**: `scripts/run_benchmark.py` automatedly rescores verified companies and compares results against the "Golden Set".
*   **Regression Testing**: Commits are checked to ensure they don't degrade accuracy (MAE metrics).

### Source Reliability

Signals are weighted based on the verifiability of their source. The system prioritizes "hard evidence" over marketing claims.

| Source Type | Verification Level | Weight | Notes |
|:---|:---|:---|:---|
| **GitHub / Open Source** | High | 2.0x | Verified code activity |
| **Job Descriptions** | High | 2.0x | Verified hiring intent (ATS integrated) |
| **AI Subdomains (ai.*)** | High | 2.0x | Dedicated infrastructure |
| **Engineering Blog** | Medium | 1.5x | Technical detailed disclosure |
| **Homepage / Press** | Low | 0.5x | Susceptible to "AI-washing" |

### Score Calculation

1. **Raw signals** are extracted from scraped content using keyword matching and heuristics.
2. Each signal category is **normalized** to a 0–100 scale based on defined caps (e.g., 30+ AI keywords = 100).
3. Category scores are **weighted and summed** to produce a final score (0–100).
4. **Signal Booster** logic rewards "spikey" excellence:
   - +10 bonus if 2+ categories score ≥ 90
   - Minimum "On Par" category if 3+ categories score ≥ 80

### Readiness Categories

| Score Range | Category | Description |
|:------------|:---------|:------------|
| **95–100** | Transformational | Industry-defining AI adoption |
| **80–94** | Leading | Strong public AI signals, dedicated teams, modern tooling |
| **60–79** | On Par | Operational AI presence, actively hiring for AI roles |
| **30–59** | Trailing | Limited AI signals, early exploration phase |
| **0–29** | Lagging | Minimal or no public AI activity |

### What Qualifies as "Leading"

A company typically scores **80+** (Leading) when it demonstrates:
- **30+** AI/ML keywords across careers and blog content
- Evidence of **agentic/autonomous systems** (workflows, orchestration, self-healing)
- Use of **5+ modern AI tools** (LangChain, PyTorch, SageMaker, etc.)
- A **dedicated AI Platform or Strategy team**
- AI adoption in **non-engineering functions** (e.g., "AI in Marketing")
- Presence of dedicated **AI/Engineering subdomains** (e.g., `ai.company.com`, `research.company.com`)

## Tech Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Scraping**: httpx, BeautifulSoup, Playwright
- **Scraping**: httpx, BeautifulSoup, Playwright
- **Discovery**: DuckDuckGo Search (ddgs), `googlesearch-python`, Subdomain Ecosystem Scanner

### Frontend
- **Framework**: Next.js 14+ (App Router)
- **Styling**: Tailwind CSS
- **Components**: Shadcn/UI

### Database
- **Development**: SQLite
- **Production**: Postgres (Neon)

## Project Structure

```
signalscore/
├── .agent/context/           # C4 architecture diagrams
├── docs/planning/            # PRD, product brief, architecture
├── execution/
│   ├── backend/              # Python/FastAPI service
│   │   ├── app/
│   │   │   ├── models/       # SQLAlchemy models (Company, Score, CompanySource)
│   │   │   ├── services/     # Scoring, Scraping, Discovery
│   │   │   └── api/          # REST endpoints
│   │   ├── scripts/          # CLI tools (rescore_company.py)
│   │   └── tests/
│   └── frontend/             # Next.js application
└── design-system/            # Theme tokens
```

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- pnpm (recommended) or npm

### Backend Setup

```bash
cd execution/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set database path
export DATABASE_URL=sqlite:///data/signalscore.db

# Run the API
uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd execution/frontend
pnpm install
pnpm dev
```

### CLI Usage

Score a company with automatic source discovery:
```bash
python scripts/rescore_company.py \
  --company "Netflix" \
  --url "https://jobs.netflix.com" \
  --research
```

Debug mode (no database save):
```bash
python scripts/rescore_company.py \
  --company "Acme Corp" \
  --url "https://acme.com/careers" \
  --debug
```

## API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `GET` | `/api/companies` | List scored companies |
| `GET` | `/api/companies/{id}` | Get company details and latest score |
| `POST` | `/api/companies/score` | Trigger scoring for a URL |

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `pytest`
4. Submit a pull request

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*For informational purposes only. Scores are derived from publicly available data.*
