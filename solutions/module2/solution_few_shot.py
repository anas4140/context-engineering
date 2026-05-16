"""
SOLUTION: Module 2 — Few-Shot Classifier with 4 Labels
========================================================
Answer key for the Module 2 Lesson 2 task:
Add a COMPLAINT label to the sentiment classifier and determine
the minimum examples needed.

Run:
    python solutions/module2/solution_few_shot.py
"""

from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
client  = Anthropic()
console = Console()
MODEL   = "claude-haiku-4-5-20251001"


def classify_4_label(review: str) -> str:
    """
    4-label classifier: POSITIVE, NEGATIVE, NEUTRAL, COMPLAINT.
    COMPLAINT = negative AND requests action/refund/escalation.

    Key insight: 4 labels need at least 1 example per label (4 minimum).
    With only 3 examples (one per original label), the model guesses
    whether NEGATIVE or COMPLAINT is appropriate.
    """
    messages = [
        # POSITIVE example
        {"role": "user",      "content": "Review: Best fridge I've ever owned, incredibly quiet.\nLabel:"},
        {"role": "assistant", "content": "POSITIVE"},

        # NEGATIVE example
        {"role": "user",      "content": "Review: The build quality is disappointing and feels cheap.\nLabel:"},
        {"role": "assistant", "content": "NEGATIVE"},

        # NEUTRAL example
        {"role": "user",      "content": "Review: It does what it says. Nothing special.\nLabel:"},
        {"role": "assistant", "content": "NEUTRAL"},

        # COMPLAINT example — distinguishes from NEGATIVE by requesting action
        {"role": "user",      "content": "Review: Broke after 2 weeks. I demand a full refund immediately.\nLabel:"},
        {"role": "assistant", "content": "COMPLAINT"},

        # The actual query
        {"role": "user",      "content": f"Review: {review}\nLabel:"},
    ]

    r = client.messages.create(model=MODEL, max_tokens=10, messages=messages)
    return r.content[0].text.strip()


TEST_REVIEWS = [
    ("Absolutely love it, best purchase this year!",                "POSITIVE"),
    ("Terrible quality, fell apart on day one.",                    "NEGATIVE"),
    ("It arrived on time and works as described.",                  "NEUTRAL"),
    ("This is broken and I want my money back NOW.",                "COMPLAINT"),
    ("Not what I expected but I'll keep it.",                       "NEUTRAL"),
    ("Zero stars. Contacted support 3 times, no response. REFUND.", "COMPLAINT"),
]


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 2 — 4-Label Few-Shot Classifier[/bold]\n")

    table = Table(title="4-Label Classification Results")
    table.add_column("Review (truncated)",  width=50)
    table.add_column("Expected",  style="cyan",  justify="center")
    table.add_column("Got",                       justify="center")
    table.add_column("Match",                     justify="center")

    correct = 0
    for review, expected in TEST_REVIEWS:
        predicted = classify_4_label(review)
        match     = predicted == expected
        correct  += int(match)
        table.add_row(
            review[:48] + "…" if len(review) > 48 else review,
            expected,
            predicted,
            "[green]✓[/green]" if match else "[red]✗[/red]"
        )

    console.print(table)
    console.print(f"\nAccuracy: {correct}/{len(TEST_REVIEWS)}")
    console.print(
        "\n[bold]Lesson:[/bold] You need at least 1 example per label. "
        "4 labels → minimum 4 examples. "
        "The COMPLAINT example is essential — without it the model defaults to NEGATIVE.\n"
    )
