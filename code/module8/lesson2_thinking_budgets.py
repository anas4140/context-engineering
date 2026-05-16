"""
Module 8, Lesson 2: Thinking Budgets & Cost Optimisation
==========================================================
Demonstrates how to choose the right thinking budget for a task by:
  - Running a query at multiple budgets and comparing output quality
  - Measuring budget utilisation to spot over/under-allocation
  - Streaming thinking + answer tokens in real time

Run:
    python code/module8/lesson2_thinking_budgets.py
"""

import os
import sys
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_THINKING

load_dotenv()
client  = Anthropic()
console = Console()

QUERY = """\
A company has three products. Product A earns $120 profit per unit with
fixed costs of $8,000/month. Product B earns $85/unit, fixed costs $5,500.
Product C earns $200/unit, fixed costs $15,000. They can produce at most
200 total units per month. How should they allocate production to maximise
profit? Provide the exact optimal mix and the maximum monthly profit.
"""

BUDGETS = [1024, 3000, 6000]


def run_with_budget(query: str, budget: int) -> dict:
    response = client.messages.create(
        model=MODEL_THINKING,
        max_tokens=budget + 2048,
        thinking={"type": "enabled", "budget_tokens": budget},
        messages=[{"role": "user", "content": query}],
    )
    thinking_text = ""
    answer_text   = ""
    for block in response.content:
        if block.type == "thinking":
            thinking_text = block.thinking
        elif block.type == "text":
            answer_text = block.text
    return {
        "budget":          budget,
        "thinking_chars":  len(thinking_text),
        "utilisation_pct": round(len(thinking_text) / (budget * 4) * 100, 1),  # ~4 chars/token
        "answer":          answer_text,
        "input_tokens":    response.usage.input_tokens,
        "output_tokens":   response.usage.output_tokens,
    }


def stream_with_thinking(query: str, budget: int):
    """Streams thinking and answer blocks, printing each as it arrives."""
    console.print(f"\n[cyan]Streaming with budget={budget} tokens...[/cyan]")
    current_type = None

    with client.messages.stream(
        model=MODEL_THINKING,
        max_tokens=budget + 2048,
        thinking={"type": "enabled", "budget_tokens": budget},
        messages=[{"role": "user", "content": query}],
    ) as stream:
        for event in stream:
            event_type = getattr(event, "type", None)
            if event_type == "content_block_start":
                current_type = event.content_block.type
                label = "[dim]Thinking:[/dim]" if current_type == "thinking" else "[green]Answer:[/green]"
                console.print(f"\n{label} ", end="")
            elif event_type == "content_block_delta":
                delta = event.delta
                if current_type == "thinking" and hasattr(delta, "thinking"):
                    console.print(delta.thinking, end="", markup=False)
                elif current_type == "text" and hasattr(delta, "text"):
                    console.print(delta.text, end="", markup=False)
    console.print()


if __name__ == "__main__":
    console.print("\n[bold]Module 8, Lesson 2 — Thinking Budgets[/bold]\n")
    console.print(Panel(QUERY, title="Problem"))

    # ── Part 1: Compare quality across budgets ───────────────────────────
    console.print(Rule("Budget comparison"))
    results = []
    for b in BUDGETS:
        console.print(f"[dim]Running budget={b}...[/dim]")
        results.append(run_with_budget(QUERY, b))

    table = Table(title="Budget comparison", show_lines=True)
    table.add_column("Budget",       justify="right")
    table.add_column("Thinking chars", justify="right")
    table.add_column("Utilisation",  justify="right")
    table.add_column("Total tokens", justify="right")
    table.add_column("Answer snippet", width=50)

    for r in results:
        util_color = "green" if 40 <= r["utilisation_pct"] <= 90 else "yellow"
        table.add_row(
            str(r["budget"]),
            str(r["thinking_chars"]),
            f"[{util_color}]{r['utilisation_pct']}%[/{util_color}]",
            str(r["input_tokens"] + r["output_tokens"]),
            r["answer"][:80].replace("\n", " "),
        )
    console.print(table)
    console.print(
        "\n[dim]Utilisation 40-90% = budget well-matched. "
        "<40% = oversized. >90% = may be undersized.[/dim]"
    )

    # ── Part 2: Live streaming ───────────────────────────────────────────
    console.print(Rule("Live streaming demo (budget=3000)"))
    stream_with_thinking("What is 17 × 23? Show your working.", budget=2000)

    console.print("\n[bold green]✓ Lesson 2 complete![/bold green]")
    console.print("Next: [italic]python code/module9/lesson1_batch_api.py[/italic]\n")
