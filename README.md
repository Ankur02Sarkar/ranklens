# RankLens: AI SEO Audit Team

RankLens is an autonomous SEO audit system built with the Google Agent Development Kit (ADK). It orchestrates a team of specialized AI agents to perform comprehensive on-page audits, analyze search engine results pages (SERPs), and generate actionable optimization reports.

## 🚀 How It Works

The workflow consists of three sequential agents:

1.  **Page Auditor**: Scrapes the target URL using Firecrawl, analyzing structural elements (headings, meta tags), content quality, and technical SEO signals.
2.  **SERP Analyst**: Identifies the primary keyword and performs a live Google Search to analyze the top 10 competitors, extracting patterns, content formats, and gaps.
3.  **Optimization Advisor**: Synthesizes findings from the audit and competitive analysis to produce a prioritized, expert-level SEO roadmap.

## 🛠️ Prerequisites

-   **Python 3.12+**
-   **Google Cloud Project** with Vertex AI API enabled (or Google AI Studio API Key)
-   **Firecrawl API Key** (for web scraping)

## 📦 Local Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Ankur02Sarkar/ranklens.git
    cd ranklens
    ```

2.  **Create a virtual environment** (optional but recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_google_api_key
    FIRECRAWL_API_KEY=your_firecrawl_api_key
    ```

5.  **Run the Agent Web UI**:
    ```bash
    adk web
    ```
    Open your browser to `http://localhost:8000`.

## 🤖 Usage

1.  Select **`SeoAuditTeam`** from the agent list in the sidebar.
2.  In the chat interface, type a command like:
    > Audit example.com
    
    (The agent will automatically prepend `https://` if omitted).

## ☁️ Deployment

### Docker

The project includes a `Dockerfile` for containerized deployment.

1.  **Build the image**:
    ```bash
    docker build -t ranklens .
    ```

2.  **Run the container**:
    ```bash
    docker run -p 8080:8080 --env-file .env ranklens
    ```

### Deploy to Render (Free Tier)

1.  Push your code to a GitHub repository.
2.  Go to [Render Dashboard](https://dashboard.render.com/).
3.  Create a **New Web Service**.
4.  Connect your repository.
5.  Select **Docker** as the Runtime.
6.  Add your Environment Variables (`GOOGLE_API_KEY`, `FIRECRAWL_API_KEY`).
7.  Deploy!

## 📂 Project Structure

```
ranklens/
├── SeoAuditTeam/       # Agent logic
│   ├── agent.py        # Main agent definitions
│   └── __init__.py
├── Dockerfile          # Docker configuration
├── requirements.txt    # Python dependencies
└── .env                # API keys (not committed)
```
