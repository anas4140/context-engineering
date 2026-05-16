"""
SOLUTION: Module 9 — Batch Evaluation Pipeline
===============================================
Runs the Module 6 evaluation suite via the Batch API instead of
synchronous calls — same quality metrics, 50% cheaper, ~3× faster at scale.

Run:
    python solutions/module9/solution_batch_eval.py
"""

import os
import sys
import time
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST, BATCH_POLL_INTERVAL

load_dotenv()
client  = Anthropic()
console = Console()

FAITHFULNESS_THRESHOLD = 0.7

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
        "name":     "Hallucinated answer",
        "question": "What is the parental leave policy?",
        "context":  "Employees receive 20 days of Paid Time Off per year.",
        "answer":   "Primary caregivers receive 16 weeks of paid parental leave.",
    },
    {
        "name":     "Off-topic answer",
        "question": "How do I submit an expense report?",
        "context":  "Submit all expenses within 30 days via Expensify.",
        "answer":   "The weather in London is typically cloudy and mild.",
    },
    {
        "name":     "Correct fallback",
        "question": "What is the bereavement leave policy?",
        "context":  "Employees receive 20 days of Paid Time Off per year.",
        "answer":   "I don't have that information in the provided documents.",
    },
]

METRIC_PROMPTS = {
    "faithfulness": lambda case: (
        f"Context: {case['context']}\nAnswer: {case['answer']}\n"
        "Rate faithfulness 0.0-1.0. Reply with ONLY a decimal."
    ),
    "relevance": lambda case: (
        f"Question: {case['question']}\nAnswer: {case['answer']}\n"
        "Rate answer relevance 0.0-1.0. Reply with ONLY a decimal."
    ),
    "precision": lambda case: (
        f"Question: {case['question']}\nContext: {case['context']}\n"
        "Rate context precision 0.0-1.0. Reply with ONLY a decimal."
    ),
}


def build_requests(test_cases: list[dict]) -> list[dict]:
    """Creates one batch request per (test_case × metric) combination."""
    requests = []
    for i, case in enumerate(test_cases):
        for metric, prompt_fn in METRIC_PROMPTS.items():
            requests.append({
                "custom_id": f"case{i}-{metric}",
                "params": {
                    "model":    MODEL_FAST,
                    "max_tokens": 10,
                    "messages": [{"role": "user", "content": prompt_fn(case)}],
                },
            })
    return requests


def parse_score(text: str) -> float:
    try:
        return float(text.strip())
    except ValueError:
        return 0.0


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 9 — Batch Evaluation Pipeline[/bold]\n")

    requests = build_requests(TEST_CASES)
    console.print(f"Submitting {len(requests)} metric requests as a single batch...")
    batch = client.messages.batches.create(requests=requests)
    console.print(f"[green]Batch ID:[/green] {batch.id}\n")

    # ── Poll ─────────────────────────────────────────────────────────────
    while batch.processing_status != "ended":
        time.sleep(BATCH_POLL_INTERVAL)
        batch = client.messages.batches.retrieve(batch.id)
        c = batch.request_counts
        console.print(f"[dim]Processing: {c.processing} | Succeeded: {c.succeeded} | Errored: {c.errored}[/dim]")

    # ── Collect scores keyed by custom_id ────────────────────────────────
    scores: dict[str, float] = {}
    for result in client.messages.batches.results(batch.id):
        if result.result.type == "succeeded":
            scores[result.custom_id] = parse_score(result.result.message.content[0].text)

    # ── Build results table ───────────────────────────────────────────────
    table = Table(title="Batch RAG Evaluation (5 test cases)", show_lines=True)
    table.add_column("Test case",     width=35)
    table.add_column("Faithfulness",  justify="right")
    table.add_column("Relevance",     justify="right")
    table.add_column("Ctx Precision", justify="right")
    table.add_column("Flag",          justify="center")

    flagged = []
    for i, case in enumerate(TEST_CASES):
        f = scores.get(f"case{i}-faithfulness", 0.0)
        r = scores.get(f"case{i}-relevance",    0.0)
        p = scores.get(f"case{i}-precision",    0.0)
        needs_flag = f < FAITHFULNESS_THRESHOLD
        if needs_flag:
            flagged.append(case["name"])
        f_str    = f"[red]{f:.2f}[/red]"    if needs_flag else f"[green]{f:.2f}[/green]"
        flag_str = "[red]⚠ LOW FAITH[/red]" if needs_flag else "[green]OK[/green]"
        table.add_row(case["name"][:34], f_str, f"{r:.2f}", f"{p:.2f}", flag_str)

    console.print(table)

    if flagged:
        console.print(f"\n[red]⚠ {len(flagged)} case(s) flagged:[/red]")
        for name in flagged:
            console.print(f"  • {name}")
    else:
        console.print("\n[green]✓ All cases passed.[/green]")

    console.print(
        f"\n[dim]Total batch requests: {len(requests)} | "
        f"Cost: ~50% of synchronous equivalent[/dim]\n"
    )
