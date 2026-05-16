"""
SOLUTION: Module 8 — Extended Thinking for Complex Reasoning
=============================================================
Answer key for the Module 8 hands-on task:
Use extended thinking to solve a multi-constraint optimisation problem,
measure budget utilisation, and decide whether thinking earned its cost.

Run:
    python solutions/module8/solution_extended_thinking.py
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

PROBLEM = """\
A project manager must schedule 5 tasks (A–E) across 3 developers (X, Y, Z).

Constraints:
- Task A takes 3 days; B takes 5 days; C takes 2 days; D takes 4 days; E takes 6 days.
- Task B must start after Task A finishes.
- Task D must start after Task C finishes.
- Developer X can only work on Tasks A or B.
- Developer Y can only work on Tasks C or D.
- Developer Z can work on any task.
- Each developer works on one task at a time.
- The goal is to finish all tasks in the minimum number of days.

What is the minimum project duration, and which developer works on which task?
Provide a Gantt-chart-style schedule and explain your reasoning.
"""


def solve_with_thinking(problem: str, budget: int) -> dict:
    response = client.messages.create(
        model=MODEL_THINKING,
        max_tokens=budget + 2048,
        thinking={"type": "enabled", "budget_tokens": budget},
        messages=[{"role": "user", "content": problem}],
    )
    thinking, answer = "", ""
    for block in response.content:
        if block.type == "thinking":
            thinking = block.thinking
        elif block.type == "text":
            answer = block.text

    thinking_tokens_est = len(thinking) // 4
    utilisation = round(thinking_tokens_est / budget * 100, 1)
    return {
        "thinking":     thinking,
        "answer":       answer,
        "usage":        response.usage,
        "utilisation":  utilisation,
    }


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 8 — Extended Thinking[/bold]\n")
    console.print(Panel(PROBLEM, title="Scheduling problem"))

    budget = THINKING_BUDGET_DEFAULT
    console.print(f"\n[dim]Running with thinking budget = {budget} tokens...[/dim]")
    result = solve_with_thinking(PROBLEM, budget)

    # ── Show scratchpad ──────────────────────────────────────────────────
    thinking_preview = result["thinking"][:1500]
    if len(result["thinking"]) > 1500:
        thinking_preview += f"\n\n... [{len(result['thinking']) - 1500} more chars] ..."
    console.print(Panel(
        thinking_preview,
        title=f"[dim]Scratchpad ({len(result['thinking'])} chars, ~{len(result['thinking'])//4} tokens)[/dim]",
        border_style="dim",
    ))

    # ── Show answer ──────────────────────────────────────────────────────
    console.print(Panel(result["answer"], title="[green]Solution[/green]"))

    # ── Budget analysis ──────────────────────────────────────────────────
    u = result["utilisation"]
    u_color = "green" if 40 <= u <= 90 else "yellow"
    verdict = (
        "Well-matched" if 40 <= u <= 90 else
        "Oversized — try halving the budget" if u < 40 else
        "May be undersized — try increasing"
    )
    console.print(
        f"\n[bold]Budget utilisation:[/bold] [{u_color}]{u}%[/{u_color}] — {verdict}"
    )
    usage = result["usage"]
    console.print(
        f"[dim]Tokens — input: {usage.input_tokens}, output: {usage.output_tokens}[/dim]"
    )
    console.print("\n[bold green]✓ Solution complete![/bold green]\n")
