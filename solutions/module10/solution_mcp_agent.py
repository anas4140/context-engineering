"""
SOLUTION: Module 10 — Full MCP Research Agent
==============================================
A multi-turn Claude agent that uses only MCP tools — no inline Python
tool definitions. Demonstrates production-style separation of concerns:
the agent code has no knowledge of tool implementations.

Run:
    python solutions/module10/solution_mcp_agent.py
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

SERVER_SCRIPT = os.path.join(os.path.dirname(__file__), "../../code/module10/mcp_server.py")
MAX_TURNS     = 8

SYSTEM_PROMPT = (
    "You are a helpful assistant with access to calculation, text analysis, "
    "and unit conversion tools. Use them whenever they would help answer accurately. "
    "Always show your reasoning before giving a final answer."
)


def mcp_to_claude_tool(mcp_tool) -> dict:
    return {
        "name":         mcp_tool.name,
        "description":  mcp_tool.description or "",
        "input_schema": mcp_tool.inputSchema,
    }


async def agent_turn(
    user_input: str,
    history: list[dict],
    claude_tools: list[dict],
    session: ClientSession,
) -> str:
    """Runs one user turn through the full ReAct loop using MCP for tool execution."""
    history.append({"role": "user", "content": user_input})
    messages = history.copy()
    turn = 0

    while turn < MAX_TURNS:
        turn += 1
        response = client.messages.create(
            model=MODEL_FAST,
            max_tokens=768,
            system=SYSTEM_PROMPT,
            tools=claude_tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            answer = next((b.text for b in response.content if hasattr(b, "text")), "")
            history.append({"role": "assistant", "content": answer})
            return answer

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    console.print(f"  [cyan]→ {block.name}({block.input})[/cyan]")
                    mcp_result  = await session.call_tool(block.name, block.input)
                    result_text = mcp_result.content[0].text if mcp_result.content else "No result"
                    console.print(f"  [dim]   {result_text}[/dim]")
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result_text,
                    })
            messages.append({"role": "user", "content": tool_results})

    return "Max turns reached."


async def main():
    console.print(Panel(
        "[bold]MCP Research Agent[/bold]\n"
        "Powered by MCP tools (calculator, word_count, unit_convert)\n\n"
        "[dim]Type your question. 'quit' to exit.[/dim]",
        title="Solution: Module 10",
        border_style="blue",
    ))

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.abspath(SERVER_SCRIPT)],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            claude_tools = [mcp_to_claude_tool(t) for t in tools_result.tools]
            console.print(
                f"[green]Connected to MCP server.[/green] "
                f"Tools: {[t['name'] for t in claude_tools]}\n"
            )

            history: list[dict] = []

            while True:
                try:
                    user_input = console.input("[bold yellow]You:[/bold yellow] ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if not user_input:
                    continue
                if user_input.lower() == "quit":
                    console.print("[dim]Goodbye![/dim]")
                    break

                console.print()
                answer = await agent_turn(user_input, history, claude_tools, session)
                console.print(Rule("Agent"))
                console.print(Panel(answer, border_style="green"))
                console.print()


if __name__ == "__main__":
    asyncio.run(main())
