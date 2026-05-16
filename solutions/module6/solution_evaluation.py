"""
SOLUTION: Module 6 — Build a Full Evaluation Suite
====================================================
Answer key for the Module 6 Lesson 1 task:
Run 5 test cases and flag any response with faithfulness < 0.7.

Run:
    python solutions/module6/solution_evaluation.py
"""

import json
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
client  = Anthropic()
console = Console()
MODEL   = "claude-haiku-4-5-20251001"


def score_faithfulness(answer: str, context: str) -> float:
    r = client.messages.create(
        model=MODEL, max_tokens=50,
        messages=[{"role": "user", "content": (
            f"Context: {context}\nAnswer: {answer}\n"
            "Rate faithfulness 0.0-1.0. Reply with ONLY a decimal."
        )}]
    )
    try:
        return float(r.content[0].text.strip())
    except ValueError:
        return 0.0


def score_relevance(answer: str, question: str) -> float:
    r = client.messages.create(
        model=MODEL, max_tokens=50,
        messages=[{"role": "user", "content": (
            f"Question: {question}\nAnswer: {answer}\n"
            "Rate answer relevance 0.0-1.0. Reply with ONLY a decimal."
        )}]
    )
    try:
        return float(r.content[0].text.strip())
    except ValueError:
        return 0.0


def score_context_precision(context: str, question: str) -> float:
    r = client.messages.create(
        model=MODEL, max_tokens=50,
        messages=[{"role": "user", "content": (
            f"Question: {question}\nContext: {context}\n"
            "Rate context precision (relevance of context to question) 0.0-1.0. "
            "Reply with ONLY a decimal."
        )}]
    )
    try:
        return float(r.content[0].text.strip())
    except ValueError:
        return 0.0


# ─────────────────────────────────────────────
#  5 Test cases covering good and bad scenarios
# ─────────────────────────────────────────────
TEST_CASES = [
    {
        "name":     "Correct answer, correct context",
        "question": "How many PTO days do employees get?",
        "context":  "Employees receive 20 days of Paid Time Off per year.",
        "answer":   "Employees receive 20 PTO days per year.",
    },
    {
        "name":     "Partially correct answer",
        "question": "Can I roll over PTO days?",
        "context":  "Up to 10 unused PTO days can be rolled over annually.",
        "answer":   "Yes, you can roll over unused PTO days up to a limit each year.",
    },
    {
        "name":     "Hallucinated answer (faithfulness should be LOW)",
        "question": "What is the parental leave policy?",
        "context":  "Employees receive 20 days of Paid Time Off per year.",   # Wrong context
        "answer":   "Primary caregivers receive 16 weeks of paid parental leave.",  # Hallucinated
    },
    {
        "name":     "Off-topic answer (relevance should be LOW)",
        "question": "How do I submit an expense report?",
        "context":  "Submit all expenses within 30 days via Expensify.",
        "answer":   "The weather in London is typically cloudy and mild.",    # Completely irrelevant
    },
    {
        "name":     "Correct fallback (no context match)",
        "question": "What is the bereavement leave policy?",
        "context":  "Employees receive 20 days of Paid Time Off per year.",   # Wrong context
        "answer":   "I don't have that information in the provided documents.",
    },
]

FAITHFULNESS_THRESHOLD = 0.7


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 6 — Full Evaluation Suite[/bold]\n")

    table = Table(title="RAG Evaluation Suite (5 test cases)", show_lines=True)
    table.add_column("Test case",        width=35)
    table.add_column("Faithfulness",     justify="right")
    table.add_column("Relevance",        justify="right")
    table.add_column("Ctx Precision",    justify="right")
    table.add_column("Flag",             justify="center")

    flagged = []
    for case in TEST_CASES:
        f = score_faithfulness(case["answer"],  case["context"])
        r = score_relevance(   case["answer"],  case["question"])
        p = score_context_precision(case["context"], case["question"])

        needs_flag = f < FAITHFULNESS_THRESHOLD
        if needs_flag:
            flagged.append(case["name"])

        flag_str = "[red]⚠ LOW FAITH[/red]" if needs_flag else "[green]OK[/green]"
        f_str    = f"[red]{f:.2f}[/red]" if f < FAITHFULNESS_THRESHOLD else f"[green]{f:.2f}[/green]"

        table.add_row(case["name"][:34], f_str, f"{r:.2f}", f"{p:.2f}", flag_str)

    console.print(table)

    if flagged:
        console.print(f"\n[red]⚠ {len(flagged)} case(s) flagged for low faithfulness:[/red]")
        for name in flagged:
            console.print(f"  • {name}")
        console.print(
            "\n[bold]Fix:[/bold] Add 'answer ONLY from context' and 'say I don't know if unsure' "
            "to the generator system prompt.\n"
        )
    else:
        console.print("\n[green]✓ All cases passed the faithfulness threshold.[/green]\n")
