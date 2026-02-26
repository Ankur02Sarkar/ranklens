from pydantic import BaseModel, Field
from typing import List, Optional
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
import os
from google.adk.agents import LlmAgent

class HeadingItem(BaseModel):
    tag: str = Field(..., description="Heading tag such as h1, h2, h3.")
    text: str = Field(..., description="Text content of the heading.")

class AuditResults(BaseModel):
    title_tag: str
    meta_description: str
    primary_heading: str
    secondary_headings: List[HeadingItem]
    word_count: Optional[int]
    content_summary: str
    link_counts: LinkCounts
    technical_findings: List[str]
    content_opportunities: List[str]

class PageAuditOutput(BaseModel):
    audit_results: AuditResults
    target_keywords: TargetKeywords

firecrawl_toolset = MCPToolset(
    connection_params=StdioServerParameters(
        command='npx',
        args=[
            "-y",  # Auto-confirm npm package installation
            "firecrawl-mcp",  # The Firecrawl MCP server package
        ],
        env={
            "FIRECRAWL_API_KEY": os.getenv("FIRECRAWL_API_KEY", "")
        }
    ),
    tool_filter=['firecrawl_scrape']  # Use only the scrape tool
)

page_auditor_agent = LlmAgent(
    name="PageAuditorAgent",
    model="gemini-2.5-flash",
    instruction="""You are Agent 1 in a sequential SEO workflow.

STEP 1: Extract the URL from the user's message
STEP 2: Call firecrawl_scrape with parameters:
  - url: <extracted URL>
  - formats: ["markdown", "html", "links"]
  - onlyMainContent: true
  - timeout: 90000

STEP 3: Analyze scraped data (title, headings, word count, links, technical issues)
STEP 4: Infer primary and secondary keywords, search intent, supporting topics
STEP 5: Return structured JSON matching PageAuditOutput schema""",
    tools=[firecrawl_toolset],
    output_schema=PageAuditOutput,
    output_key="page_audit"
)