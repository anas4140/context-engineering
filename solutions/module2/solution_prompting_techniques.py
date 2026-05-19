"""
SOLUTION: Module 2, Lesson 2 — Prompting Techniques
======================================================
Demonstrates zero-shot, few-shot, chain-of-thought, and XML-structured
prompting on the same task so you can compare output quality directly.

Run:
    python solutions/module2/solution_prompting_techniques.py
"""

import os
import sys
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

TASK = "Classify the sentiment of this review: 'The battery died after 3 months. Support never responded.'"


def call(system: str, user: str) -> str:
    r = client.messages.create(
        model=MODEL_FAST, max_tokens=256,
        system=system,
        messages=[{"role": "user", "content": user}]
    )
    return r.content[0].text.strip()


# ── 1. Zero-shot ─────────────────────────────────────────────────────────
def zero_shot(task: str) -> str:
    return call("You are a helpful assistant.", task)


# ── 2. Few-shot ──────────────────────────────────────────────────────────
FEW_SHOT_EXAMPLES = """
Classify sentiment as: Positive / Negative / Neutral / Mixed

Examples:
Review: "Fast shipping and great quality!"
Sentiment: Positive

Review: "It broke after one week but support replaced it quickly."
Sentiment: Mixed

Review: "Does exactly what it says."
Sentiment: Neutral

Now classify:
"""

def few_shot(task: str) -> str:
    return call("You are a sentiment classifier.", FEW_SHOT_EXAMPLES + task)


# ── 3. Chain-of-thought ──────────────────────────────────────────────────
def chain_of_thought(task: str) -> str:
    return call(
        "You are a careful analyst. Think step by step before classifying.",
        f"{task}\n\nThink through this carefully before answering:\n"
        "1. What is the customer saying about the product?\n"
        "2. What is the customer saying about support?\n"
        "3. What is the overall emotional tone?\n"
        "4. Final classification: Positive / Negative / Neutral / Mixed"
    )


# ── 4. XML-structured ────────────────────────────────────────────────────
def xml_structured(task: str) -> str:
    return call(
        "You are a precise classifier. Always respond in the XML format shown.",
        f"""Classify the review sentiment. Respond ONLY in this exact format:

<analysis>
  <product_sentiment>positive|negative|neutral</product_sentiment>
  <support_sentiment>positive|negative|neutral|not_mentioned</support_sentiment>
  <overall>Positive|Negative|Neutral|Mixed</overall>
  <confidence>high|medium|low</confidence>
  <reason>one sentence</reason>
</analysis>

Review: {task}"""
    )


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 2 — Prompting Techniques[/bold]\n")
    console.print(f"[yellow]Task:[/yellow] {TASK}\n")

    techniques = [
        ("Zero-shot",         zero_shot),
        ("Few-shot",          few_shot),
        ("Chain-of-thought",  chain_of_thought),
        ("XML-structured",    xml_structured),
    ]

    for name, fn in techniques:
        console.print(Rule(name))
        result = fn(TASK)
        console.print(Panel(result, title=f"[cyan]{name}[/cyan]"))
        console.print()

    console.print("[bold]Key insight:[/bold] Same model, same task — the prompt structure "
                  "determines output structure and reasoning depth.\n")
    console.print("[bold green]✓ Solution complete![/bold green]\n")
