"""
Module 5, Lesson 1: The ReAct Pattern
=======================================
ReAct = Reason + Act. The model reasons about what to do, acts by calling
a tool, observes the result, and reasons again — until it has the answer.

This lesson shows the pattern from scratch with a single tool, making the
Reason → Act → Observe loop explicit before introducing the full agent loop.

Run:
    python code/module5/lesson1_react_pattern.py
"""

import os
import sys
import json
import math
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
client  = Anthropic()
console = Console()

# ── One tool: calculator ─────────────────────────────────────────────────
TOOL = {
    "name": "calculator",
    "description": "Evaluates a Python math expression.",
    "input_schema": {
        "type": "object",
        "properties": {"expression": {"type": "string"}},
        "required": ["expression"],
    },
}


def calculator(expression: str) -> str:
    allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    try:
        return f"Result: {eval(expression, {'__builtins__': {}}, allowed)}"
    except Exception as e:
        return f"Error: {e}"


def react_loop(query: str) -> str:
    """
    Explicit ReAct loop — prints each phase so you can see the pattern.

    Turn 0:  User query → Claude reasons and decides to call a tool
    Turn 1+: Tool result → Claude reasons again (may call more tools or answer)
    Final:   Claude returns end_turn with a text answer
    """
    messages = [{"role": "user", "content": query}]
    turn = 0

    console.print(f"\n[bold yellow]Query:[/bold yellow] {query}\n")

    while True:
        turn += 1
        console.print(Rule(f"Turn {turn}"))

        response = client.messages.create(
            model=MODEL_FAST,
            max_tokens=512,
            tools=[TOOL],
            messages=messages,
        )

        # ── REASON phase: show what the model is thinking ────────────────
        for block in response.content:
            if hasattr(block, "text") and block.text:
                console.print(f"[cyan]Reason:[/cyan] {block.text}")

        # ── Check stop reason ────────────────────────────────────────────
        if response.stop_reason == "end_turn":
            answer = next(b.text for b in response.content if hasattr(b, "text"))
            console.print(f"\n[green]Answer:[/green] {answer}")
            return answer

        # ── ACT phase: execute the tool the model chose ──────────────────
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                console.print(f"\n[magenta]Act:[/magenta]    {block.name}({json.dumps(block.input)})")
                result = calculator(**block.input)

                # ── OBSERVE phase: show what we got back ─────────────────
                console.print(f"[dim]Observe:[/dim] {result}")

                tool_results.append({
                    "type":        "tool_result",
                    "tool_use_id": block.id,
                    "content":     result,
                })

        messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    console.print("\n[bold]Module 5, Lesson 1 — The ReAct Pattern[/bold]")
    console.print("[dim]Watch: Reason → Act → Observe → repeat[/dim]\n")

    queries = [
        "What is 17 × 23?",
        "A circle has radius 7. What is its area? Use π.",
        "If I invest $1000 at 5% annual interest for 10 years, what is the final amount?",
    ]

    for query in queries:
        react_loop(query)
        console.print()

    console.print("[bold green]✓ Lesson 1 complete![/bold green]")
    console.print("Next: [italic]python code/module5/lesson2_tool_design.py[/italic]\n")
