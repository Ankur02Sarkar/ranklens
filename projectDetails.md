# RankLens — Complete Project Documentation

> **AI-Powered On-Page SEO Audit & Optimization Platform**

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Who Is It For?](#who-is-it-for)
- [How It Works](#how-it-works)
- [Agent Architecture](#agent-architecture)
  - [Agent 1: Page Auditor](#agent-1-page-auditor)
  - [Agent 2: SERP Analyst](#agent-2-serp-analyst)
  - [Agent 3: Optimization Advisor](#agent-3-optimization-advisor)
  - [Orchestration: Sequential Agent](#orchestration-sequential-agent)
- [Output Schemas (Structured Data)](#output-schemas-structured-data)
- [Tools & Integrations](#tools--integrations)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Environment Variables](#environment-variables)
- [Local Development Setup](#local-development-setup)
- [Deployment](#deployment)
- [Usage](#usage)
- [Features in Detail](#features-in-detail)
- [Report Structure](#report-structure)

---

## Project Overview

**RankLens** is an autonomous, multi-agent SEO audit system built on the **Google Agent Development Kit (ADK)**. It orchestrates a team of three specialized AI agents in a sequential pipeline to perform comprehensive on-page SEO audits, analyze search engine results pages (SERPs), and generate actionable, prioritized optimization reports — all from a single URL input.

The system combines:

- **Web scraping** (via Firecrawl MCP) for real-time page analysis
- **Live Google Search** for competitive SERP research
- **Google Gemini 2.5 Flash** for intelligent analysis and report generation
- **Structured Pydantic schemas** for type-safe, machine-readable output at each stage

Users interact with RankLens through the **ADK Web UI**, a built-in chat interface that comes with the Google ADK framework. Simply select the "SeoAuditTeam" agent and type a command like `Audit example.com` to kick off a full SEO audit.

---

## Who Is It For?

- **SEO Professionals** — Get deep, data-backed page audits with competitive analysis and prioritized recommendations in seconds instead of hours
- **Content Marketers** — Understand how your content stacks up against top-ranking competitors and identify content gaps and opportunities
- **Web Developers** — Detect technical SEO issues (missing alt text, heading hierarchy problems, link issues) automatically
- **Startup Founders & Indie Hackers** — Run professional-grade SEO audits without hiring an agency
- **Digital Marketing Agencies** — Generate white-label SEO audit reports for clients at scale
- **Bloggers & Content Creators** — Optimize individual pages for better search visibility

---

## How It Works

The entire workflow is triggered by a single user message (e.g., `"Audit mindmyjob.com"`) and runs through three agents sequentially:

```
User Input (URL)
       │
       ▼
┌──────────────────────┐
│  Agent 1: Page       │  ──► Firecrawl MCP (scrapes URL)
│  Auditor             │  ──► Outputs: PageAuditOutput (JSON)
│                      │      • audit_results
│                      │      • target_keywords
└──────────┬───────────┘
           │ (state['page_audit'])
           ▼
┌──────────────────────┐
│  Agent 2: SERP       │  ──► Google Search (live SERP)
│  Analyst             │  ──► Outputs: SerpAnalysis (JSON)
│                      │      • top_10_results
│                      │      • title_patterns, themes
│                      │      • differentiation opportunities
└──────────┬───────────┘
           │ (state['serp_analysis'])
           ▼
┌──────────────────────┐
│  Agent 3: Optimization│  ──► Reads both previous outputs
│  Advisor             │  ──► Outputs: Markdown Report
│                      │      • Executive Summary
│                      │      • Technical Findings
│                      │      • Keyword Analysis
│                      │      • Competitive SERP Analysis
│                      │      • Prioritized Recommendations
│                      │      • Next Steps
└──────────────────────┘
           │
           ▼
    Final SEO Report (Markdown)
```

**Key Design Principle:** Each agent focuses on a single responsibility and passes structured data to the next agent via the ADK state mechanism (`output_key`). The first two agents produce machine-readable JSON; the final agent synthesizes everything into a human-readable Markdown report.

---

## Agent Architecture

### Agent 1: Page Auditor

| Property | Value |
|---|---|
| **Name** | `PageAuditorAgent` |
| **Type** | `LlmAgent` |
| **Model** | `gemini-2.5-flash` |
| **Tools** | Firecrawl MCP Toolset (`firecrawl_scrape`) |
| **Output Schema** | `PageAuditOutput` (JSON) |
| **Output Key** | `page_audit` |

**What It Does:**

1. **Extracts the URL** from the user's message, auto-prepending `https://` if no protocol is specified
2. **Scrapes the target page** using the Firecrawl MCP tool with parameters:
   - `formats`: `["markdown", "html", "links"]`
   - `onlyMainContent`: `true`
   - `timeout`: 90000ms (90 seconds)
3. **Analyzes the scraped content** to extract:
   - Title tag, meta description, H1 heading
   - Secondary headings (H2-H4) in reading order
   - Word count of main content
   - Content summary
   - Internal, external, and broken link counts
   - Technical SEO issues (missing alt text, slow LCP, etc.)
   - Content opportunities and gaps
4. **Infers keyword focus** from the page content:
   - Primary keyword (1-3 words)
   - 2-5 secondary keywords
   - Search intent (informational, transactional, navigational, commercial)
   - 3-5 supporting topics
5. **Returns structured JSON** conforming to the `PageAuditOutput` schema

---

### Agent 2: SERP Analyst

| Property | Value |
|---|---|
| **Name** | `SerpAnalystAgent` |
| **Type** | `LlmAgent` |
| **Model** | `gemini-2.5-flash` |
| **Tools** | `google_search_tool` (AgentTool wrapping a helper agent) |
| **Output Schema** | `SerpAnalysis` (JSON) |
| **Output Key** | `serp_analysis` |

**What It Does:**

1. **Reads the primary keyword** from the previous agent's output via `state['page_audit']['target_keywords']['primary_keyword']`
2. **Executes a live Google Search** using a helper sub-agent (`perform_google_search`) that wraps the ADK's built-in `google_search` tool
3. **Parses the top 10 organic results**, extracting for each:
   - Rank position
   - Title
   - URL
   - Snippet
   - Content type (blog post, landing page, tool, directory, video, etc.)
4. **Analyzes competitive patterns:**
   - Title patterns and common phrases (e.g., "Best", "Top 10", "Free", year references)
   - Dominant content formats (guides, listicles, comparison pages, tool directories)
   - People Also Ask questions (inferred from snippets)
   - Key recurring themes across top results
   - Differentiation opportunities — gaps not covered by competitors

**Helper Agent:** The Google Search is executed through a dedicated `search_executor_agent` (`perform_google_search`) that is wrapped as an `AgentTool`. This pattern isolates the search execution from the analysis logic.

---

### Agent 3: Optimization Advisor

| Property | Value |
|---|---|
| **Name** | `OptimizationAdvisorAgent` |
| **Type** | `LlmAgent` |
| **Model** | `gemini-2.5-flash` |
| **Tools** | None (synthesis only) |
| **Output** | Markdown report (free-form, not JSON) |

**What It Does:**

1. **Reviews all accumulated data** from both previous agents:
   - From `state['page_audit']`: Title tag, meta description, H1, word count, headings structure, link counts, technical findings, content opportunities, keywords
   - From `state['serp_analysis']`: Top 10 competitors, title patterns, content formats, key themes, differentiation opportunities
2. **Generates a comprehensive Markdown report** with specific, data-cited recommendations
3. **Prioritizes recommendations** using P0/P1/P2 priority levels with rationale, expected impact, and effort estimates
4. **Produces the final user-facing output** — this is the only agent whose output the user sees directly

---

### Orchestration: Sequential Agent

| Property | Value |
|---|---|
| **Name** | `SeoAuditTeam` |
| **Type** | `SequentialAgent` |
| **Sub-Agents** | `PageAuditorAgent` → `SerpAnalystAgent` → `OptimizationAdvisorAgent` |

The `SequentialAgent` from Google ADK ensures agents run in strict order, with shared state passing data between them. The `seo_audit_team` is exposed as the `root_agent` for the ADK runtime.

---

## Output Schemas (Structured Data)

The project uses **Pydantic v2** models to enforce structured, type-safe output from AI agents. This ensures consistent, machine-readable data flows between agents.

### PageAuditOutput (Agent 1 Output)

```
PageAuditOutput
├── audit_results: AuditResults
│   ├── title_tag: str
│   ├── meta_description: str
│   ├── primary_heading: str (H1)
│   ├── secondary_headings: List[HeadingItem]
│   │   ├── tag: str (h2, h3, h4)
│   │   └── text: str
│   ├── word_count: Optional[int]
│   ├── content_summary: str
│   ├── link_counts: LinkCounts
│   │   ├── internal: Optional[int]
│   │   ├── external: Optional[int]
│   │   ├── broken: Optional[int]
│   │   └── notes: Optional[str]
│   ├── technical_findings: List[str]
│   └── content_opportunities: List[str]
└── target_keywords: TargetKeywords
    ├── primary_keyword: str
    ├── secondary_keywords: List[str]
    ├── search_intent: str
    └── supporting_topics: List[str]
```

### SerpAnalysis (Agent 2 Output)

```
SerpAnalysis
├── primary_keyword: str
├── top_10_results: List[SerpResult]
│   ├── rank: int
│   ├── title: str
│   ├── url: str
│   ├── snippet: str
│   └── content_type: str
├── title_patterns: List[str]
├── content_formats: List[str]
├── people_also_ask: List[str]
├── key_themes: List[str]
└── differentiation_opportunities: List[str]
```

### OptimizationRecommendation (Used in Agent 3 Report)

```
OptimizationRecommendation
├── priority: str (P0, P1, P2)
├── area: str (content, technical, UX, etc.)
├── recommendation: str
├── rationale: str
├── expected_impact: str
└── effort: str (low, medium, high)
```

---

## Tools & Integrations

### Firecrawl MCP (Web Scraping)

RankLens uses the **Firecrawl MCP server** for web scraping, connected via the **Model Context Protocol (MCP)**.

| Property | Detail |
|---|---|
| **Connection Type** | `StdioServerParameters` (spawns a child process) |
| **Command** | `bunx firecrawl-mcp` |
| **Environment** | Inherits all env vars + `FIRECRAWL_API_KEY` |
| **Filtered Tools** | Only `firecrawl_scrape` is exposed (other Firecrawl tools are filtered out) |
| **Scrape Parameters** | `formats: ["markdown", "html", "links"]`, `onlyMainContent: true`, `timeout: 90000` |

**Why MCP?** The Model Context Protocol allows the agent to use Firecrawl as a standardized tool server. The MCP server runs as a separate process (`bunx firecrawl-mcp`) and communicates via stdio, keeping the architecture modular and extensible.

**Why Bun?** Bun is used as the JavaScript runtime to execute the `firecrawl-mcp` package. It's installed globally in the Docker image via `bun install -g firecrawl-mcp` for production, and locally via `bunx` (which auto-installs on first use) for development.

### Google Search (SERP Research)

The built-in `google_search` tool from `google.adk.tools` provides live Google Search results. It's wrapped in a helper `LlmAgent` (`perform_google_search`) and then exposed as an `AgentTool` — this pattern is used because ADK's AgentTool interface allows one agent to invoke another agent as if it were a tool.

### Google Gemini 2.5 Flash

All three agents use **Gemini 2.5 Flash** (`gemini-2.5-flash`) as their LLM model. This model provides:

- Fast inference for agentic workflows
- Strong structured output adherence (JSON schemas)
- Good reasoning for analysis and synthesis

---

## Tech Stack

| Technology | Purpose |
|---|---|
| **Google ADK (Agent Development Kit)** | Multi-agent orchestration framework (SequentialAgent, LlmAgent, AgentTool) |
| **Google Gemini 2.5 Flash** | LLM for all agents (analysis, synthesis, report generation) |
| **Firecrawl** | Web scraping service (via MCP server) |
| **MCP (Model Context Protocol)** | Tool integration protocol (Firecrawl MCP server connected via stdio) |
| **Google Search** | Live SERP analysis (ADK built-in tool) |
| **Python 3.12** | Runtime language |
| **Pydantic v2 (≥2.7.0)** | Data validation and structured output schemas |
| **uv** | Python package manager (project setup) |
| **Bun** | JavaScript runtime for executing `firecrawl-mcp` MCP server |
| **Docker** | Containerization for deployment |
| **Render** | Cloud hosting platform (Docker-based deployment) |
| **ADK Web UI** | Built-in chat interface from Google ADK (`adk web` command) |

---

## Project Structure

```
ranklens/
├── SeoAuditTeam/               # Agent package
│   ├── __init__.py             # Package init (imports agent module)
│   ├── agent.py                # All agent definitions, schemas, tools (358 lines)
│   └── __pycache__/            # Python bytecode cache
├── .adk/                       # ADK runtime artifacts
│   └── artifacts/              # Agent execution artifacts
├── .venv/                      # Python virtual environment (uv-managed)
├── .env                        # Environment variables (GOOGLE_API_KEY, FIRECRAWL_API_KEY)
├── .gitignore                  # Git ignore rules
├── .dockerignore               # Docker ignore rules
├── .python-version             # Python version pin (3.12)
├── Dockerfile                  # Docker build configuration
├── README.md                   # Project documentation
├── pyproject.toml              # uv project configuration
└── requirements.txt            # Python dependencies (google-adk, pydantic)
```

**Key File: `agent.py`** — This single file (358 lines) contains the entire application logic:

- 8 Pydantic output schema models
- 1 MCP toolset configuration (Firecrawl)
- 1 helper search agent + AgentTool wrapper
- 3 specialized LlmAgents with detailed instructions
- 1 SequentialAgent orchestrator
- Root agent export for ADK runtime

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GOOGLE_API_KEY` | ✅ | Google AI Studio API key for Gemini model access and Google Search |
| `FIRECRAWL_API_KEY` | ✅ | Firecrawl API key for web scraping via MCP server |

Both must be set in a `.env` file locally or as environment variables in the deployment platform (Render).

---

## Local Development Setup

### Prerequisites

- Python 3.12+
- Bun (JavaScript runtime, for Firecrawl MCP)
- Google Cloud Project with Vertex AI API enabled (or Google AI Studio API Key)
- Firecrawl API Key

### Setup Steps

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Ankur02Sarkar/ranklens.git
   cd ranklens
   ```

2. **Set up the Python environment with uv:**

   ```bash
   uv venv
   source .venv/bin/activate
   uv pip install -r requirements.txt
   ```

3. **Configure environment variables:**

   ```bash
   # Create .env file
   echo "GOOGLE_API_KEY=your_google_api_key" > .env
   echo "FIRECRAWL_API_KEY=your_firecrawl_api_key" >> .env
   ```

4. **Run the ADK Web UI:**

   ```bash
   adk web
   ```

   Opens at `http://localhost:8000`

---

## Deployment

### Docker Build

The `Dockerfile` uses a multi-stage approach:

1. **Base Image:** `python:3.12-slim`
2. **System Dependencies:** `curl`, `unzip` (for Bun installation)
3. **Bun Installation:** Installs Bun globally at `/root/.bun`
4. **Python Dependencies:** `pip install` from `requirements.txt`
5. **Firecrawl MCP Pre-install:** `bun install -g firecrawl-mcp` — pre-installs the MCP server globally to avoid runtime delays
6. **Application Code:** Copies all project files
7. **Runtime Command:** `adk web --port 8080 --host 0.0.0.0`

```bash
# Build
docker build -t ranklens .

# Run
docker run -p 8080:8080 --env-file .env ranklens
```

### Render Deployment (Production)

RankLens is deployed on **Render** using Docker:

1. Push code to GitHub
2. Create a new Web Service on Render Dashboard
3. Connect the GitHub repository
4. Select **Docker** as the Runtime
5. Add environment variables (`GOOGLE_API_KEY`, `FIRECRAWL_API_KEY`)
6. Deploy — Render auto-builds the Docker image and serves on port 8080

---

## Usage

1. Open the ADK Web UI (locally at `http://localhost:8000` or the Render-deployed URL)
2. Select **`SeoAuditTeam`** from the agent list in the sidebar
3. Type a command in the chat:

   ```
   Audit example.com
   ```

   Or with full URL:

   ```
   Audit https://www.example.com/specific-page
   ```

4. The system will:
   - **Agent 1:** Scrape the URL with Firecrawl and produce a structured audit
   - **Agent 2:** Search Google for the primary keyword and analyze competitors
   - **Agent 3:** Generate a comprehensive SEO optimization report

5. The final Markdown report appears in the chat

---

## Features in Detail

### On-Page SEO Audit

- **Title Tag Analysis** — Extracts and evaluates the full title tag with length and keyword presence
- **Meta Description Review** — Checks meta description for length, keyword inclusion, and call-to-action
- **Heading Structure** — Maps the complete H1-H4 hierarchy in reading order
- **Content Depth** — Word count estimation and main content summarization
- **Link Profile** — Counts and categorizes internal, external, and broken links
- **Technical SEO** — Detects issues like missing alt text, slow LCP, render-blocking resources, etc.
- **Content Gaps** — Identifies missing topics or underserved content areas

### Keyword Intelligence

- **Primary Keyword Detection** — Infers the most likely target keyword (1-3 words) from page content
- **Secondary Keywords** — Identifies 2-5 related supporting keywords
- **Search Intent Classification** — Categorizes as informational, transactional, navigational, or commercial
- **Topic Cluster Mapping** — Lists supporting entities and topics that reinforce the keyword strategy

### Competitive SERP Analysis

- **Top 10 Competitor Profiling** — Analyzes each top-ranking result with title, URL, snippet, and content type
- **Title Pattern Recognition** — Identifies common phrases and structures in competitor titles
- **Content Format Analysis** — Maps dominant formats (guides, listicles, comparisons, tools, videos)
- **People Also Ask** — Surfaces related questions for content expansion
- **Theme Extraction** — Highlights recurring themes and angles across top results
- **Differentiation Opportunities** — Identifies gaps and unique angles not covered by competitors

### Prioritized Optimization Roadmap

- **P0/P1/P2 Priority System** — Each recommendation is ranked by urgency
- **Area Classification** — Recommendations categorized by area (content, technical, UX)
- **Data-Cited Rationale** — Every recommendation references specific audit or SERP data
- **Impact Assessment** — Expected impact on SEO or user metrics
- **Effort Estimation** — Relative effort required (low/medium/high)
- **Measurement Plan** — Suggested KPIs and tracking approach
- **Implementation Timeline** — Timeline suggestions for executing the roadmap

---

## Report Structure

The final output from Agent 3 follows this Markdown structure:

```
# SEO Audit Report

## 1. Executive Summary
   - Page being audited
   - Primary keyword focus
   - Key strengths and weaknesses (2-3 paragraphs)

## 2. Technical & On-Page Findings
   - Current title tag + suggestions
   - Current meta description + suggestions
   - H1 and heading structure analysis
   - Word count and content depth
   - Link profile (internal/external counts)
   - Technical issues found

## 3. Keyword Analysis
   - Primary keyword
   - Secondary keywords
   - Search intent
   - Supporting topics

## 4. Competitive SERP Analysis
   - Top competitor strategies
   - Common title patterns
   - Dominant content formats
   - Key themes in top results
   - Content gaps and opportunities

## 5. Prioritized Recommendations
   - P0 (Critical) actions
   - P1 (Important) actions
   - P2 (Nice-to-have) actions
   Each with: recommendation, rationale, expected impact, effort

## 6. Next Steps
   - Measurement plan
   - Timeline suggestions
```

---

_Last Updated: February 2026_
_Framework: Google ADK (Agent Development Kit)_
_AI Model: Google Gemini 2.5 Flash_
_Scraping: Firecrawl via MCP_
_Language: Python 3.12_
_Package Manager: uv_
_Deployment: Docker on Render_
_Repository: github.com/Ankur02Sarkar/ranklens_
