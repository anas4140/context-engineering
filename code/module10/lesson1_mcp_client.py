"""
Module 10, Lesson 1: MCP Client — Claude + MCP Tools
======================================================
Starts the local MCP server as a subprocess, discovers its tools,
converts them to Claude's format, and runs an agent loop that calls
tools via MCP instead of inline Python functions.

Run:
    python code/module10/lesson1_mcp_client.py
"""

import os
import sys
import asyncio
from anthropic import Anthropic
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
client  = Anthropic()
console = Console()

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "mcp_server.py")


def mcp_to_claude_tool(mcp_tool) -> dict:
    """Converts an MCP Tool object to a Claude tool definition dict."""
    return {
        "name":         mcp_tool.name,
        "description":  mcp_tool.description or "",
        "input_schema": mcp_tool.inputSchema,
    }


async def run_agent(user_query: str, session: ClientSession) -> str:
    """
    Single-turn agent: discovers MCP tools, sends query to Claude,
    executes any tool calls via the MCP session, returns final answer.
    """
    # ── 1. Discover tools from the MCP server ────────────────────────────
    tools_result  = await session.list_tools()
    claude_tools  = [mcp_to_claude_tool(t) for t in tools_result.tools]
    console.print(f"[dim]Discovered {len(claude_tools)} MCP tools: "
                  f"{[t['name'] for t in claude_tools]}[/dim]")

    # ── 2. Send query to Claude ───────────────────────────────────────────
    messages = [{"role": "user", "content": user_query}]
    response = client.messages.create(
        model=MODEL_FAST,
        max_tokens=512,
        tools=claude_tools,
        messages=messages,
    )

    # ── 3. Execute tool calls via MCP ─────────────────────────────────────
    while response.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                console.print(f"  [cyan]MCP call:[/cyan] {block.name}({block.input})")
                mcp_result = await session.call_tool(block.name, block.input)
                result_text = mcp_result.content[0].text if mcp_result.content else "No result"
                console.print(f"  [dim]→ {result_text}[/dim]")
                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     result_text,
                })

        messages.append({"role": "user", "content": tool_results})
        response = client.messages.create(
            model=MODEL_FAST,
            max_tokens=512,
            tools=claude_tools,
            messages=messages,
        )

    return response.content[0].text if response.content else "No response"


async def main():
    console.print("\n[bold]Module 10, Lesson 1 — Claude + MCP Tools[/bold]\n")

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[SERVER_SCRIPT],
    )

    queries = [
        "What is the square root of 1764 plus 15 squared?",
        "How many words are in this sentence: 'The quick brown fox jumps over the lazy dog'?",
        "Convert 100 km to miles, then convert 25 celsius to fahrenheit.",
    ]

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            console.print("[green]MCP server connected.[/green]\n")

            for query in queries:
                console.print(Rule())
                console.print(f"[yellow]Q:[/yellow] {query}")
                answer = await run_agent(query, session)
                console.print(Panel(answer, title="[green]Answer[/green]"))

    console.print("\n[bold green]✓ Lesson 1 complete![/bold green]")
    console.print("Next: [italic]solutions/module10/solution_mcp_agent.py[/italic]\n")


if __name__ == "__main__":
    asyncio.run(main())
