"""
SOLUTION: Module 1, Lesson 2 — Token Economics
===============================================
Demonstrates token counting, cost estimation at scale, and the
compounding savings from prompt optimisation.

Run:
    python solutions/module1/solution_economics.py
"""

import os
import sys
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
client  = Anthropic()
console = Console()

# ── Three prompt styles — minimal vs medium vs verbose ────────────────────
PROMPTS = {
    "Minimal":  "Help with customer issues.",
    "Medium":   (
        "You are a customer support agent for ACME Inc. "
        "Resolve customer issues clearly and concisely."
    ),
    "Verbose":  (
        "You are a friendly, empathetic, and highly experienced customer support specialist "
        "for ACME Inc., a leading provider of smart home appliances. "
        "Your primary goal is to resolve every customer issue on the first contact. "
        "Always: acknowledge the customer's frustration, provide a specific solution, "
        "offer a follow-up step, and close with a positive statement. "
        "Never: escalate unnecessarily, use technical jargon, or promise things you cannot deliver."
    ),
    "Ultra-minimal": "Support agent.",
}

HAIKU_INPUT_PRICE  = 0.80  / 1_000_000   # $ per token
HAIKU_OUTPUT_PRICE = 4.00  / 1_000_000


def count_tokens(text: str) -> int:
    """Uses tiktoken (cl100k_base) to count tokens."""
    try:
        import tiktoken
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        return len(text) // 4   # rough fallback


def estimate_monthly_cost(tokens: int, daily_requests: int, price_per_token: float) -> float:
    return tokens * daily_requests * 30 * price_per_token


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 1 — Token Economics[/bold]\n")

    USER_MSG     = "My order hasn't arrived and it's been 2 weeks."
    DAILY_REQS   = [1_000, 10_000, 100_000]

    # ── Token count table ─────────────────────────────────────────────────
    table = Table(title="System Prompt Comparison", show_lines=True)
    table.add_column("Style",      width=15)
    table.add_column("Tokens",     justify="right")
    table.add_column("1K reqs/day", justify="right")
    table.add_column("10K reqs/day", justify="right")
    table.add_column("100K reqs/day", justify="right")

    for name, prompt in PROMPTS.items():
        tok  = count_tokens(prompt)
        costs = [f"${estimate_monthly_cost(tok, r, HAIKU_INPUT_PRICE):.2f}/mo"
                 for r in DAILY_REQS]
        table.add_row(name, str(tok), *costs)

    console.print(table)

    # ── Live demo ─────────────────────────────────────────────────────────
    console.print("\n[bold]Live response quality comparison:[/bold]\n")
    for name, prompt in list(PROMPTS.items())[:2]:   # just minimal vs medium
        response = client.messages.create(
            model=MODEL_FAST, max_tokens=128,
            system=prompt,
            messages=[{"role": "user", "content": USER_MSG}]
        )
        console.print(f"[cyan]{name}:[/cyan] {response.content[0].text[:200]}\n")

    # ── Savings calculation ────────────────────────────────────────────────
    tok_verbose      = count_tokens(PROMPTS["Verbose"])
    tok_medium       = count_tokens(PROMPTS["Medium"])
    saved_per_call   = tok_verbose - tok_medium
    saved_monthly_10k = estimate_monthly_cost(saved_per_call, 10_000, HAIKU_INPUT_PRICE)
    console.print(
        f"[green]Trimming from Verbose to Medium saves {saved_per_call} tokens/call "
        f"= ${saved_monthly_10k:.2f}/month at 10K daily requests.[/green]\n"
    )
    console.print("[bold green]✓ Solution complete![/bold green]\n")
