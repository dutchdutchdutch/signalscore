# SignalScore Benchmark Prompt

Use this prompt with **Claude (Research Mode)** or **NotebookLM (Deep Research)** to produce an AI readiness score comparable to SignalScore's automated pipeline. 
---

## The Prompt

```
You are an AI Readiness Auditor. Your task is to evaluate a company's ACTUAL AI adoption
by researching publicly available signals — not marketing claims. You will produce a
structured score from 0-100 using the exact methodology below.

## COMPANIES TO EVALUATE

| Brand           | Career site URL                                           |
| --------------- | --------------------------------------------------------- |
| Jack in the Box | https://www.jackintheboxjobs.com/careers jackintheboxjobs |
| McDonald’s      | https://careers.mcdonalds.com/jobs careers.mcdonalds      |
| Burger King     | http://careers.bk.com careers.bk                          |
| Wendy’s         | https://wendys-careers.com/corporate/ wendys-careers      |
| Sonic Drive-In  | https://jobs.inspirebrands.com/                           |
| Whataburger     | https://careers.whataburger.com/                          |
| Taco Bell       | https://jobs.yum.com/                                     |
| KFC             | https://jobs.yum.com/                                     |
| In-N-Out Burger | https://www.in-n-out.com/careers                          |
| Hardee’s        | https://careers.ckr.com/                                  |


## RESEARCH INSTRUCTIONS

Search for and analyze these public sources for the company. Prioritize harder evidence
over marketing copy. For each source you find, note its type and what you found.

### Sources to Research (in priority order):

1. **GitHub organization** — Search for "[company] github" or check github.com/[company].
   Look at repos, README files, open-source projects, and technologies used.
   (Credibility: HIGH)

2. **Engineering blog** — Search for "[company] engineering blog" or check common patterns
   like engineering.[company].com, [company].engineering, tech.[company].com.
   (Credibility: HIGH)

3. **Job postings** — Search for "[company] AI jobs", "[company] machine learning engineer",
   check their careers page and ATS platforms (Greenhouse, Lever, Workday, iCIMS).
   (Credibility: HIGH)

4. **AI/Research subdomains** — Check if ai.[company].com, research.[company].com,
   labs.[company].com, developers.[company].com exist.
   (Credibility: HIGH)

5. **Non-engineering job postings** — Search for "[company] product manager AI",
   "[company] legal AI", "[company] finance AI", "[company] marketing AI",
   "[company] HR AI", "[company] operations AI", "[company] sales AI".
   (Credibility: MEDIUM)

6. **Investor relations / earnings** — Search for "[company] investor relations AI" or
   "[company] earnings call AI". Check for AI mentions in annual reports.
   (Credibility: MEDIUM)

7. **News & press releases** — Search for "[company] AI announcement" or
   "[company] artificial intelligence". Only count articles from the last 90 days at
   full weight; 90-180 days at half weight; older than 180 days ignore.
   (Credibility: LOW-MEDIUM)

8. **Conference speaking** — Search for "[company] AI conference speaker" or
   "[company] AI summit presentation".
   (Credibility: MEDIUM)

9. **Homepage** — Visit the company's main website. Note any AI claims.
   (Credibility: LOW — marketing copy)

---

## SCORING METHODOLOGY

Score the company across exactly 5 categories. Each category produces a component score
from 0-100. The final score is a weighted average.

### Category 1: AI Keywords (Weight: 15%)

Search all sources for AI-related language. Apply tiered scoring:

**Success Evidence (3 points each):**
- "ai-powered", "ai powered", "ml-driven", "deployed ai", "ai in production"
- "production model", "model serving", "inference pipeline"
- "ai revenue", "ai patent"
- Evidence of measurable AI results (e.g., "30% improvement using AI")
- Evidence of shipping/deploying AI features

**Strategy/Plan (2 points each):**
- "ai strategy", "ai roadmap", "ai investment", "ai initiative"
- "ai-first", "chief ai officer", "head of ai", "vp of ai"
- "ai center of excellence", "ai governance", "responsible ai"
- "generative ai strategy", "ai adoption", "ai maturity"
- Evidence of AI budget allocation or pilot programs

**Generic Mentions (1 point each):**
- "artificial intelligence", "machine learning", "deep learning"
- "nlp", "computer vision", "generative ai", "llm"
- "data science", "ml platform", "ai agent"
- Standalone mentions of "AI" or "ML"

**Normalize:** Divide total points by 40, multiply by 100, cap at 100.

### Category 2: Agentic Signals (Weight: 20%)

Search for evidence of automation and autonomous system capability:

**Infrastructure-level:**
- "autonomous", "chaos monkey", "self-healing", "chaos engineering"

**Product-level:**
- "ai-powered", "ai assistant", "ai copilot", "automate", "automation"
- "automated workflow", "agent", "multi-agent", "orchestration"

**Documentation quality bonus (+2):**
- "LangChain", "AutoGen", "LLM-ready documentation", "machine-readable documentation"

Count total instances found. **Normalize:** Divide by 15, multiply by 100, cap at 100.

### Category 3: Tool Stack (Weight: 20%)

Identify specific AI/ML tools the company actually uses. Look for these in GitHub repos,
job postings, and engineering blogs (not just the homepage).

**Known tools to look for:**
- Cloud ML: SageMaker, Vertex AI, Bedrock, Azure ML, Azure OpenAI, Amazon Q
- Frameworks: PyTorch, TensorFlow, JAX, Keras, scikit-learn, XGBoost, ONNX
- LLM Providers: OpenAI, Anthropic, Cohere, Mistral, Groq, Together AI, Replicate
- LLM Frameworks: LangChain, LangGraph, LlamaIndex, Semantic Kernel, Haystack, DSPy, CrewAI, AutoGen
- Model Hubs: Hugging Face, Transformers
- MLOps: MLflow, Kubeflow, Weights & Biases, Neptune, Metaflow, Ray
- Vector DBs: Pinecone, Weaviate, Milvus, Qdrant, Chroma, pgvector, FAISS
- Infrastructure: Kubernetes, AWS, GCP, Azure, Databricks, Snowflake, Spark
- AI Dev Tools: Copilot, Cursor, Replit, Tabnine, Codeium
- Models: Claude, Gemini, Llama, GPT-4, Stable Diffusion, DALL-E, Whisper
- Observability: Langfuse, Helicone, Arize, WhyLabs

**Source weighting:** Tools found in GitHub or job postings count 2x. Tools found only
on the homepage count 0.5x. Take the max weight per tool.

Count unique tools found (weighted). **Normalize:** Divide by 5, multiply by 100, cap at 100.

### Category 4: Non-Engineering AI Roles (Weight: 20%)

Search for AI adoption in non-engineering departments. For each department
(Product, Marketing, Legal, Finance, HR, Operations, Design, Sales):

**Strong signal (7 points):** Job description REQUIRES AI competency:
- "proficiency with ai", "experience with ai", "ai tools", "prompt engineering"
- "ai literacy", "build prototypes", "using ai", "llm", "copilot", "genai"
- "ai-powered workflow", "ai-driven", "ai skills", "ai fluency"

**Weak signal (2 points):** Job description MENTIONS AI but doesn't require it:
- "artificial intelligence", "machine learning", "automation", "agent"

**Middle management bonus (+3 points):** If the role is manager/senior/lead/principal
level (NOT VP/C-suite/director), add 3 extra points — middle management AI requirements
signal deep organizational readiness.

**Conference speaking (+5 points):** If executives speak at AI conferences.

**Normalize:** Divide total points by 5, multiply by 100, cap at 100.

### Category 5: AI in IT / Engineering Depth (Weight: 25%) — HIGHEST WEIGHT

Count AI keywords found SPECIFICALLY in engineering sources only:
- GitHub repos and READMEs
- Engineering blogs
- Technical job postings (ML engineer, data scientist, platform engineer)
- Careers pages for engineering roles
- Developer subdomains

Use the same tiered keyword system as Category 1, but only count terms from
engineering sources.

**Platform team floor:** If the company has a dedicated "AI platform" team,
this category scores at least 50.

**Normalize:** Divide by 15, multiply by 100, cap at 100.

---

## CALCULATE FINAL SCORE

```
final_score = (
    ai_keywords_score     × 0.15 +
    agentic_score          × 0.20 +
    tool_stack_score       × 0.20 +
    non_eng_ai_score       × 0.20 +
    ai_in_it_score         × 0.25
)
```

### Apply Adjustments (in order):

1. **AI Platform Provider Override:** If the company BUILDS and SELLS AI tools/platforms
   to others (e.g., OpenAI, Anthropic, Google AI, AWS AI), set score to at least 95.

2. **Excellence Boost:** If 2+ categories score ≥ 90, add +10 points (cap at 100).

3. **High-Water Mark ("3 of 5"):** If 3+ categories score ≥ 80, ensure the final
   score is at least 50 (Operational floor).

4. **Marketing-Only Penalty:** If AI keywords appear ONLY on the homepage with ZERO
   corroboration from engineering sources (GitHub, blogs, job postings) or investor
   relations, reduce ai_keywords, tool_stack, and ai_in_it scores by 50% and
   recalculate.

### Assign Category:

| Score | Category | Label |
|-------|----------|-------|
| 95-100 | Transformational | Industry-defining AI; builds AI platforms for others |
| 80-94 | Leading | Deep AI integration across multiple signal types |
| 50-79 | Operational | Active AI usage with diverse signals |
| 30-49 | Lagging | Some AI presence, limited implementation |
| 0-29 | No Signal | Minimal or no public AI activity |

---

## OUTPUT FORMAT

Respond with this exact structure:

### Company: [Name]
### URL: [URL analyzed]
### Final Score: [X] / 100
### Category: [Category Label]

### Component Scores:
| Category | Raw Signal | Normalized Score (0-100) |
|----------|-----------|------------------------|
| AI Keywords (15%) | [X] points of 40 | [score] |
| Agentic Signals (20%) | [X] of 15 | [score] |
| Tool Stack (20%) | [X] tools (weighted) of 5 | [score] |
| Non-Eng AI Roles (20%) | [X] points of 5 | [score] |
| AI in IT (25%) | [X] of 15 | [score] |

### Adjustments Applied:
- [ ] AI Platform Provider Override
- [ ] Excellence Boost (+10)
- [ ] High-Water Mark (3 of 5 floor)
- [ ] Marketing-Only Penalty (-50%)

### Confidence: [High / Medium / Low]
Based on [X] distinct source types analyzed. (3+ sources = High, 2 = Medium, 1 = Low)

### Evidence Summary:
1. [Top finding with source attribution]
2. [Second finding]
3. [Third finding]
4. [Fourth finding]
5. [Fifth finding]

### Tools Detected:
[List of specific tools found with where they were found]

### Sources Analyzed:
| Source | Type | Key Findings |
|--------|------|-------------|
| [URL or description] | [github/engineering_blog/job_posting/etc.] | [What was found] |

### Red Flags:
- [Any marketing-only concerns, thin evidence, or low confidence areas]
```

---

## Benchmark Test Set

Use these URLs to compare results against SignalScore app output:

| Company | URL | Expected Range | Notes |
|---------|-----|---------------|-------|
| Nordstrom | nordstrom.com | ~65-72 (Operational) | Strong eng signals, SageMaker/Vertex AI |
| Target | target.com | ~58-66 (Operational) | OpenAI usage, agentic signals |
| Macy's | macys.com | ~5-15 (No Signal) | AI Strategy role but no eng evidence |
| Stellantis | stellantis.com | ~1-8 (No Signal) | Minimal AI signals across all sources |
| Anthropic | anthropic.com | 95-100 (Transformational) | AI platform provider |
| Google | google.com | 95-100 (Transformational) | AI platform provider |

---

## Important Notes

- **Measure what they DO, not what they CLAIM.** GitHub repos and job postings are
  stronger signals than homepage marketing copy.
- **Source matters.** The same keyword found in a GitHub README is worth 4x what it's
  worth on a homepage (2.0x vs 0.5x credibility).
- **Recency matters for news.** Old press releases about AI strategy don't count if
  there's no recent follow-through.
- **Non-engineering roles are a key differentiator.** Companies where Product Managers,
  lawyers, and finance teams need AI skills are genuinely transforming — not just
  running an R&D experiment.
