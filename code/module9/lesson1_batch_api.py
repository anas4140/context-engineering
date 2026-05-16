"""
Module 9, Lesson 1: The Message Batches API
============================================
Submits a batch of evaluation requests, polls for completion,
and processes results — at 50% lower cost than synchronous calls.

Run:
    python code/module9/lesson1_batch_api.py
"""

import os
import sys
import time
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST, BATCH_POLL_INTERVAL

load_dotenv()
client  = Anthropic()
console = Console()

# ─────────────────────────────────────────────
#  10 evaluation test cases — diverse topics
# ─────────────────────────────────────────────
TEST_CASES = [
    {"id": "fact-001", "question": "What is the speed of light in m/s?"},
    {"id": "fact-002", "question": "In what year did World War II end?"},
    {"id": "math-001", "question": "What is the square root of 2,025?"},
    {"id": "math-002", "question": "If a rectangle is 7m × 13m, what is its area?"},
    {"id": "logic-001", "question": "All mammals are warm-blooded. Dolphins are mammals. Are dolphins warm-blooded?"},
    {"id": "logic-002", "question": "If it rains, the ground gets wet. The ground is wet. Did it necessarily rain?"},
    {"id": "code-001",  "question": "In Python, what does `list(range(5))` return?"},
    {"id": "code-002",  "question": "What does the SQL keyword DISTINCT do?"},
    {"id": "sci-001",   "question": "What gas do plants absorb during photosynthesis?"},
    {"id": "sci-002",   "question": "What is the atomic number of carbon?"},
]


def build_batch_requests(test_cases: list[dict]) -> list[dict]:
    return [
        {
            "custom_id": case["id"],
            "params": {
                "model":     MODEL_FAST,
                "max_tokens": 128,
                "messages":  [{"role": "user", "content": case["question"]}],
            },
        }
        for case in test_cases
    ]


def poll_until_done(batch_id: str) -> object:
    """Polls batch status every BATCH_POLL_INTERVAL seconds until complete."""
    while True:
        batch = client.messages.batches.retrieve(batch_id)
        counts = batch.request_counts
        console.print(
            f"  [dim]Status: {batch.processing_status} | "
            f"Succeeded: {counts.succeeded} | "
            f"Processing: {counts.processing} | "
            f"Errored: {counts.errored}[/dim]"
        )
        if batch.processing_status == "ended":
            return batch
        time.sleep(BATCH_POLL_INTERVAL)


if __name__ == "__main__":
    console.print("\n[bold]Module 9, Lesson 1 — Message Batches API[/bold]\n")

    # ── Submit batch ─────────────────────────────────────────────────────
    requests = build_batch_requests(TEST_CASES)
    console.print(f"Submitting batch of {len(requests)} requests...")
    batch = client.messages.batches.create(requests=requests)
    console.print(f"[green]Batch created:[/green] {batch.id}")

    # ── Poll for completion ───────────────────────────────────────────────
    console.print("\nPolling for completion (check every 10s)...")
    batch = poll_until_done(batch.id)

    # ── Retrieve and display results ─────────────────────────────────────
    console.print("\n[bold]Results:[/bold]")
    table = Table(title="Batch evaluation results", show_lines=True)
    table.add_column("ID",       width=12)
    table.add_column("Question", width=40)
    table.add_column("Answer",   width=40)
    table.add_column("Status",   justify="center", width=10)

    id_to_question = {c["id"]: c["question"] for c in TEST_CASES}
    succeeded = errored = 0

    for result in client.messages.batches.results(batch.id):
        question = id_to_question.get(result.custom_id, "?")
        if result.result.type == "succeeded":
            answer = result.result.message.content[0].text[:80].replace("\n", " ")
            table.add_row(result.custom_id, question[:39], answer, "[green]OK[/green]")
            succeeded += 1
        else:
            table.add_row(
                result.custom_id, question[:39],
                str(result.result.error.type), "[red]ERR[/red]"
            )
            errored += 1

    console.print(table)
    console.print(
        f"\n[green]{succeeded} succeeded[/green], [red]{errored} errored[/red]"
    )
    console.print(
        "\n[dim]Tip: batch requests are billed at 50% of the standard rate.[/dim]"
    )
    console.print("\n[bold green]✓ Lesson 1 complete![/bold green]")
    console.print("Next: [italic]python code/module9/lesson2_streaming.py[/italic]\n")
