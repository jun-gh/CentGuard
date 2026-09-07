"""
Direct data endpoint for the frontend's spending chart.

Deliberately bypasses Claude/the MCP tool-calling loop — this is just a
straight DB query, so there's no reason to spend API tokens or add latency
asking an LLM to fetch numbers we can look up directly. We reuse the same
underlying function the MCP tool calls, just without the LLM round-trip.
"""
from fastapi import APIRouter, Query

from app.mcp_server import tools as finance_tools

router = APIRouter(prefix="/api", tags=["spending"])


@router.get("/spending-summary")
def spending_summary(month: str | None = Query(default=None, description="YYYY-MM, defaults to current month")):
    return finance_tools.get_spending_by_category(month)