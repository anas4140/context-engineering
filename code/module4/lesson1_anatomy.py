"""
Module 4, Lesson 1: Context Window Anatomy
===========================================
Visualises what occupies the context window and demonstrates the
"lost in the middle" problem — where content placed in the middle
of a long context is attended to less than content at the edges.

Run:
    python code/module4/lesson1_anatomy.py
"""

import os
import tiktoken
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.bar import Bar

load_dotenv()
client  = Anthropic()
console = Console()
enc     = tiktoken.get_encoding("cl100k_base")
MODEL   = "claude-haiku-4-5-20251001"


def tok(text: str) -> int:
    return len(enc.encode(text))


# ─────────────────────────────────────────────
#  DEMO 1: Visualise the context window budget
#  Shows how different layers consume tokens.
# ─────────────────────────────────────────────
def visualise_budget(
    system_prompt:    str,
    conversation:     list[dict],
    rag_context:      str,
    user_query:       str,
    context_limit:    int = 200_000,
    output_reserve:   int = 2_048,
) -> None:
    """
    Prints a token budget breakdown for a single request.
    """
    system_tokens  = tok(system_prompt)
    history_tokens = sum(tok(m["content"]) for m in conversation)
    rag_tokens     = tok(rag_context)
    query_tokens   = tok(user_query)
    total_input    = system_tokens + history_tokens + rag_tokens + query_tokens
    available      = context_limit - output_reserve
    pct            = round(total_input / available * 100, 1)

    table = Table(title="Context Window Budget")
    table.add_column("Layer",         style="cyan")
    table.add_column("Tokens",        justify="right")
    table.add_column("% of budget",   justify="right")

    rows = [
        ("System prompt (Layers 1-3, 5, 10)", system_tokens),
        ("Conversation history (Layer 6)",    history_tokens),
        ("RAG context (Layer 8)",             rag_tokens),
        ("User query (Layer 11)",             query_tokens),
    ]
    for label, tokens in rows:
        pct_row = round(tokens / available * 100, 1)
        table.add_row(label, str(tokens), f"{pct_row}%")

    table.add_section()
    color = "green" if pct < 70 else "yellow" if pct < 90 else "red"
    table.add_row(
        "[bold]Total input[/bold]",
        f"[{color}]{total_input}[/{color}]",
        f"[{color}]{pct}%[/{color}]"
    )
    console.print(table)

    if pct > 80:
        console.print(
            f"[yellow]⚠ Warning: {pct}% of budget used. "
            "Consider compressing history or reducing RAG chunks.[/yellow]"
        )


# ─────────────────────────────────────────────
#  DEMO 2: Lost-in-the-Middle experiment
#  Hides a target fact at different positions
#  in a list and asks Claude to find it.
#  Demonstrates reduced attention in the middle.
# ─────────────────────────────────────────────
def lost_in_middle_demo(position: str = "start") -> str:
    """
    Places a target fact (employee ID) at the start, middle, or end
    of a long list of decoy facts, then asks Claude to find it.

    Args:
        position: "start", "middle", or "end"
    """
    target_fact = "Employee ID 7742 has the highest performance rating (9.8/10)."

    # 20 decoy facts that look similar
    decoys = [
        f"Employee ID {1000 + i * 37} has a performance rating of {5.0 + (i % 5) * 0.4:.1f}/10."
        for i in range(20)
    ]

    if position == "start":
        facts = [target_fact] + decoys
    elif position == "end":
        facts = decoys + [target_fact]
    else:  # middle
        mid = len(decoys) // 2
        facts = decoys[:mid] + [target_fact] + decoys[mid:]

    facts_text = "\n".join(facts)

    system = "You are a data analyst. Answer questions using ONLY the facts provided."
    user   = (
        f"Here is a list of employee performance facts:\n\n{facts_text}\n\n"
        "Which employee has the highest performance rating? "
        "State the employee ID and rating only."
    )

    r = client.messages.create(
        model=MODEL, max_tokens=64, system=system,
        messages=[{"role": "user", "content": user}]
    )
    return r.content[0].text.strip()


if __name__ == "__main__":
    console.print("\n[bold]Module 4, Lesson 1: Context Window Anatomy[/bold]\n")

    # ── Demo 1: Budget visualisation ──────────
    console.print("[bold cyan]Demo 1: Context Window Budget Breakdown[/bold cyan]")

    visualise_budget(
        system_prompt=(
            "You are an expert HR assistant for ACME Inc. Answer employee questions "
            "accurately using only the retrieved context. Cite your sources. "
            "If the answer is not in the context, say so."
        ),
        conversation=[
            {"role": "user",      "content": "Hi, I need help with my benefits."},
            {"role": "assistant", "content": "Of course! What would you like to know?"},
            {"role": "user",      "content": "Can I add my partner to my health plan?"},
            {"role": "assistant", "content": "Yes, dependants can be added during open enrolment each November."},
        ],
        rag_context=(
            "[Source: employee_handbook.pdf, p.18]\n"
            "Health insurance covers the employee and eligible dependants. "
            "Open enrolment is each November. Mid-year changes are only allowed "
            "after qualifying life events such as marriage or birth of a child."
        ),
        user_query="When exactly is the open enrolment window?",
    )

    # ── Demo 2: Lost in the middle ────────────
    console.print("\n[bold cyan]Demo 2: Lost-in-the-Middle Effect[/bold cyan]")
    console.print("Placing the same target fact at start, middle, and end of a 21-item list...\n")

    results = {}
    for pos in ["start", "middle", "end"]:
        answer = lost_in_middle_demo(pos)
        found  = "7742" in answer
        results[pos] = (answer, found)
        status = "[green]✓ Found[/green]" if found else "[red]✗ Missed[/red]"
        console.print(f"  Position [cyan]{pos:6}[/cyan]: {status} — {answer[:80]}")

    console.print(
        "\n[dim]If the middle result missed or was less confident, "
        "that's the lost-in-the-middle effect in action.[/dim]"
    )

    console.print("\n[bold green]✓ Lesson 1 complete![/bold green]")
    console.print("Next: [italic]python code/module4/lesson2_compression.py[/italic]\n")
