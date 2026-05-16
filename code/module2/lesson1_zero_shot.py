"""
Module 2, Lesson 1: Prompt Taxonomy — Zero-shot Baseline
=========================================================
Establishes zero-shot as the baseline and shows when it succeeds vs fails,
motivating the need for more advanced techniques in Lesson 2.

Run:
    python code/module2/lesson1_zero_shot.py
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv()
client  = Anthropic()
console = Console()
MODEL   = "claude-haiku-4-5-20251001"


def zero_shot(task: str, system: str = "You are a helpful assistant.") -> str:
    r = client.messages.create(
        model=MODEL, max_tokens=256, system=system,
        messages=[{"role": "user", "content": task}]
    )
    return r.content[0].text.strip()


# ─────────────────────────────────────────────
#  DEMO 1: Tasks where zero-shot works well
#  Simple, common tasks the model has seen
#  thousands of times during training.
# ─────────────────────────────────────────────
ZERO_SHOT_WINS = [
    ("Translation",     "Translate to Spanish: 'The meeting is at 3pm tomorrow.'"),
    ("Capitalisation",  "Capitalise the first letter of each word: 'the quick brown fox'"),
    ("Simple maths",    "What is 15% of 240?"),
    ("Basic summary",   "Summarise in one sentence: 'Paris is the capital of France and is known for the Eiffel Tower, its cuisine, and its art museums.'"),
]

# ─────────────────────────────────────────────
#  DEMO 2: Tasks where zero-shot FAILS
#  These need either examples (few-shot) or
#  explicit format instructions (clarity).
# ─────────────────────────────────────────────
ZERO_SHOT_FAILS = [
    (
        "Inconsistent format",
        "Classify this review: 'Loved it, very fast shipping!' Output only the sentiment.",
        "Should output exactly: POSITIVE — but may say 'Positive', 'positive sentiment', etc."
    ),
    (
        "Ambiguous task",
        "Summarise this: 'Q3 revenue was $4.2M, up 12% YoY. Operating costs rose 8%.'",
        "Length and format are undefined — every run may differ."
    ),
    (
        "Domain-specific format",
        "Write a SOAP note for: 'Patient presents with 3-day headache, no fever, no nausea.'",
        "Without a role or examples, the model may not know the exact SOAP format."
    ),
]


if __name__ == "__main__":
    console.print("\n[bold]Module 2, Lesson 1: Zero-shot Baseline[/bold]\n")

    # ── Where zero-shot works ─────────────────
    console.print("[bold cyan]Tasks where zero-shot works well:[/bold cyan]")
    win_table = Table(show_header=True)
    win_table.add_column("Task",   style="cyan", width=20)
    win_table.add_column("Output", width=55)

    for label, task in ZERO_SHOT_WINS:
        output = zero_shot(task)
        win_table.add_row(label, output[:100])
    console.print(win_table)

    # ── Where zero-shot fails ─────────────────
    console.print("\n[bold cyan]Tasks where zero-shot is unreliable:[/bold cyan]")
    for label, task, reason in ZERO_SHOT_FAILS:
        output = zero_shot(task)
        console.print(f"\n  [yellow]{label}[/yellow]")
        console.print(f"  Task:   {task[:80]}")
        console.print(Panel(output[:200], title="Output"))
        console.print(f"  [dim]Problem: {reason}[/dim]")

    console.print(
        "\n[bold]Takeaway:[/bold] Zero-shot is the right starting point — "
        "but for format-sensitive or domain-specific tasks, add few-shot "
        "examples or explicit format instructions.\n"
    )
    console.print("[bold green]✓ Lesson 1 complete![/bold green]")
    console.print("Next: [italic]python code/module2/lesson2_prompting_techniques.py[/italic]\n")
