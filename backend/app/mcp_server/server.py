"""
The MCP server: exposes CentWhisper's finance tools over the Model Context
Protocol so any MCP-compatible client (Claude Desktop, Claude Code, or our
own claude_client.py) can call them.

Run standalone for local testing / Claude Desktop integration:
    python -m app.mcp_server.server

In production, our FastAPI backend spawns this as a subprocess and talks to
it over stdio (see claude_client.py).
"""
from typing import Optional

#from mcp.server.fastmcp import FastMCP
from mcp.server.mcpserver import MCPServer

from app.mcp_server import tools as finance_tools

#mcp = FastMCP("centwhisper-finance")
mcp = MCPServer("centwhisper-finance")


@mcp.tool()
def get_transactions(start_date: str, end_date: str, category: Optional[str] = None) -> list[dict]:
    """
    Get raw transactions between two dates (inclusive).

    Args:
        start_date: ISO date, e.g. "2026-08-01"
        end_date: ISO date, e.g. "2026-08-31"
        category: optional category filter, e.g. "Food & Dining"
    """
    return finance_tools.get_transactions(start_date, end_date, category)


@mcp.tool()
def get_spending_by_category(month: Optional[str] = None) -> dict:
    """
    Get total spending broken down by category for a given month.

    Args:
        month: "YYYY-MM" format, e.g. "2026-08". Omit for the current month.
    """
    return finance_tools.get_spending_by_category(month)


@mcp.tool()
def get_monthly_summary(month: Optional[str] = None) -> dict:
    """
    Get income, expenses, and net savings for a given month.

    Args:
        month: "YYYY-MM" format, e.g. "2026-08". Omit for the current month.
    """
    return finance_tools.get_monthly_summary(month)


@mcp.tool()
def detect_anomalies(threshold_multiplier: float = 2.5, lookback_days: int = 90) -> list[dict]:
    """
    Find transactions that are unusually large compared to typical spending
    in their own category, within a recent lookback window.

    Args:
        threshold_multiplier: how many times above the category's median
            counts as "unusual" (default 2.5x).
        lookback_days: how far back to look (default 90 days).
    """
    return finance_tools.detect_anomalies(threshold_multiplier, lookback_days)


if __name__ == "__main__":
    mcp.run()
