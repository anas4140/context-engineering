"""
Module 8, Lesson 1: Extended Thinking
======================================
Demonstrates Claude's extended thinking feature: a private reasoning scratchpad
that runs before the visible answer. Shows how to enable it, read thinking blocks,
and compare answers with and without thinking on a complex problem.

Run:
    python code/module8/lesson1_extended_thinking.py
"""

import os
import sys
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_THINKING, THINKING_BUDGET_DEFAULT

load_dotenv()
client  = Anthropic()
console = Console()


# ─────────────────────────────────────────────
#  A problem that genuinely benefits from
#  extended reasoning (multi-step logic)
# ─────────────────────────────────────────────
HARD_PROBLEM = """\
A farmer has 17 sheep. All but 9 die. How many sheep are left?

Then: if each surviving sheep produces 3 kg of wool per month, and wool
sells for $4.50/kg with a 12% sales tax included in the price, how much
does the farmer earn (before tax) over a quarter? Show every step.
"""

SIMPLE_PROBLEM = "What is the capital of France?"


def answer_without_thinking(query: str) -> str:
    """Standard call — no reasoning scratchpad."""
    response = client.messages.create(
        model=MODEL_THINKING,
        max_tokens=512,
        messages=[{"role": "user", "content": query}],
    )
    return response.content[0].text


def answer_with_thinking(query: str, budget: int = THINKING_BUDGET_DEFAULT) -> dict:
    """
    Extended thinking call.
    Returns both the scratchpad text and the final answer.
    """
    response = client.messages.create(
        model=MODEL_THINKING,
        max_tokens=budget + 2048,  # must cover budget + output
        thinking={"type": "enabled", "budget_tokens": budget},
        messages=[{"role": "user", "content": query}],
    )

    result = {"thinking": "", "answer": "", "usage": response.usage}
    for block in response.content:
        if block.type == "thinking":
            result["thinking"] = block.thinking
        elif block.type == "text":
            result["answer"] = block.text
    return result


if __name__ == "__main__":
    console.print("\n[bold]Module 8, Lesson 1 — Extended Thinking[/bold]\n")

    # ── Demo 1: simple question (thinking not needed) ────────────────────
    console.print(Rule("Simple question (no thinking needed)"))
    console.print(f"[yellow]Q:[/yellow] {SIMPLE_PROBLEM}")
    simple_result = answer_with_thinking(SIMPLE_PROBLEM, budget=1024)
    console.print(f"[dim]Scratchpad length: {len(simple_result['thinking'])} chars[/dim]")
    console.print(Panel(simple_result["answer"], title="Answer"))

    # ── Demo 2: hard problem — compare with/without thinking ────────────
    console.print(Rule("Hard multi-step problem"))
    console.print(f"[yellow]Q:[/yellow] {HARD_PROBLEM}")

    console.print("\n[cyan]Without extended thinking:[/cyan]")
    plain_answer = answer_without_thinking(HARD_PROBLEM)
    console.print(Panel(plain_answer, title="Standard answer"))

    console.print("\n[cyan]With extended thinking (budget = 4000 tokens):[/cyan]")
    thinking_result = answer_with_thinking(HARD_PROBLEM, budget=4000)

    console.print(Panel(
        thinking_result["thinking"][:1000] + ("..." if len(thinking_result["thinking"]) > 1000 else ""),
        title="[dim]Scratchpad (truncated)[/dim]",
        border_style="dim",
    ))
    console.print(Panel(thinking_result["answer"], title="[green]Answer with thinking[/green]"))

    usage = thinking_result["usage"]
    console.print(
        f"\n[dim]Tokens — input: {usage.input_tokens}, "
        f"output: {usage.output_tokens}[/dim]"
    )

    console.print("\n[bold green]✓ Lesson 1 complete![/bold green]")
    console.print("Next: [italic]python code/module8/lesson2_thinking_budgets.py[/italic]\n")
