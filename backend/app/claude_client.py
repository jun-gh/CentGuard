"""
This is where the two certifications ("Claude with Anthropic API" and
"Introduction to MCP") actually meet:

1. We spawn our MCP server (app/mcp_server/server.py) as a subprocess and
   connect to it over stdio.
2. We ask it what tools it has (`list_tools`) and translate that into the
   `tools=[...]` format the Anthropic Messages API expects.
3. We send the user's message to Claude along with those tool definitions.
4. If Claude responds with `stop_reason == "tool_use"`, we actually execute
   the requested tool(s) against the MCP server, feed the results back to
   Claude as `tool_result` blocks, and let it continue — looping until it
   gives a final text answer.

A fresh MCP session is opened per request for simplicity in this demo. For
a production system you'd keep a long-lived MCP session/pool instead of
spawning a subprocess on every request.
"""
import sys
from contextlib import AsyncExitStack

from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.config import ANTHROPIC_API_KEY, CLAUDE_MODEL

import datetime

SYSTEM_PROMPT = f"""You are CentWhisper, a friendly personal finance copilot for a user in the \
Philippines. Today's date is {datetime.date.today().isoformat()}. You have tools that let you \
look up the user's REAL transaction data — always use them instead of guessing or making up \
numbers. Amounts are in PHP (₱). When the user says "last month", "this month", "last week", \
etc., compute the actual YYYY-MM (or date range) yourself from today's date before calling a \
tool — the tools only accept explicit dates, not relative phrases. Be concise, use actual \
figures from the tools, and flag anything that looks worth the user's attention (e.g. \
anomalies, high spending categories). Keep answers short — a few sentences or a short list, \
not a full report, unless the user asks for detail."""

MCP_SERVER_PARAMS = StdioServerParameters(
    command=sys.executable,
    args=["-m", "app.mcp_server.server"],
)

anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)


def _mcp_tools_to_anthropic_format(mcp_tools) -> list[dict]:
    """Convert MCP's tool listing into the shape Anthropic's Messages API expects."""
    return [
        {
            "name": t.name,
            "description": t.description or "",
            "input_schema": t.input_schema,
        }
        for t in mcp_tools
    ]


async def chat_with_claude(user_message: str, history: list[dict] | None = None) -> dict:
    """
    Runs one full turn of the conversation, including any tool-use round trips.
    Returns {"reply": str, "tools_used": [str, ...]}.
    """
    messages = list(history or [])
    messages.append({"role": "user", "content": user_message})

    tools_used: list[str] = []

    async with AsyncExitStack() as stack:
        read, write = await stack.enter_async_context(stdio_client(MCP_SERVER_PARAMS))
        session: ClientSession = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()

        mcp_tools = (await session.list_tools()).tools
        anthropic_tools = _mcp_tools_to_anthropic_format(mcp_tools)

        # Loop until Claude stops asking for tools and gives a final answer.
        for _ in range(6):  # hard cap so a runaway tool loop can't hang a request
            response = anthropic_client.messages.create(
                model=CLAUDE_MODEL,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                tools=anthropic_tools,
                messages=messages,
            )

            if response.stop_reason != "tool_use":
                final_text = "".join(
                    block.text for block in response.content if block.type == "text"
                )
                return {"reply": final_text, "tools_used": tools_used}

            # Claude wants to call one or more tools. Execute each, collect results.
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue

                tools_used.append(block.name)
                result = await session.call_tool(block.name, block.input)
                result_text = "".join(
                    c.text for c in result.content if getattr(c, "type", None) == "text"
                )

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result_text,
                        "is_error": bool(result.is_error),
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        return {
            "reply": "Sorry, that took more tool calls than expected — could you rephrase your question?",
            "tools_used": tools_used,
        }
