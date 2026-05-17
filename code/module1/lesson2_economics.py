"""
Module 1, Lesson 2: The Evolution and Economics of Context
==========================================================
This script demonstrates token counting and cost estimation.
Understanding token costs is essential for building efficient applications.

Run:
    python code/module1/lesson2_economics.py
"""

import os
import tiktoken
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
client = Anthropic()
console = Console()

# ─────────────────────────────────────────────
#  Token counting helper
#  tiktoken is OpenAI's tokeniser but gives a
#  close approximation for Claude too.
# ─────────────────────────────────────────────
def count_tokens(text: str) -> int:
    """
    Estimates the number of tokens in a string.
    Rule of thumb: 1 token ≈ 4 characters ≈ 0.75 words.
    """
    # cl100k_base is the GPT-4 / Claude tokeniser family
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


def estimate_cost(input_tokens: int, output_tokens: int,
                  model: str = "claude-haiku-4-5-20251001") -> float:
    """
    Estimates API cost in USD for a single call.
    Prices as of mid-2025 — always check console.anthropic.com for current rates.
    """
    # Prices per million tokens (MTok)
    pricing = {
        "claude-haiku-4-5-20251001":  {"input": 0.80,  "output": 4.00},
        "claude-sonnet-4-6": {"input": 3.00,  "output": 15.00},
        "claude-opus-4-7":   {"input": 15.00, "output": 75.00},
    }
    rates = pricing.get(model, pricing["claude-haiku-4-5-20251001"])
    input_cost  = (input_tokens  / 1_000_000) * rates["input"]
    output_cost = (output_tokens / 1_000_000) * rates["output"]
    return input_cost + output_cost


# ─────────────────────────────────────────────
#  Demo: compare three different system prompts
#  to show how prompt length affects token use
# ─────────────────────────────────────────────
PROMPTS = {
    "Minimal": "You are a helpful assistant.",

    "Medium": (
        "You are a helpful, friendly customer support assistant for ACME Inc. "
        "Always be polite, concise, and accurate. If you don't know the answer, "
        "say so honestly rather than guessing."
    ),

    "Verbose": (
        "You are a highly experienced, empathetic, and professional customer "
        "support specialist for ACME Inc., a leading global technology company. "
        "Your role is to provide exceptional assistance to customers experiencing "
        "issues with their ACME products. You should always greet the customer "
        "warmly, acknowledge their frustration, provide clear step-by-step "
        "solutions, and follow up to ensure their issue is resolved. Use a "
        "friendly, professional tone at all times. Never guess — if you are "
        "unsure, escalate to a human agent. Always end responses by asking if "
        "there is anything else you can help with today."
    ),
}

USER_MESSAGE = "My fridge isn't making ice. What should I do?"


def run_token_comparison():
    """
    Calls the API with each system prompt and prints a cost comparison table.
    """
    table = Table(title="Token Economics: System Prompt Comparison")
    table.add_column("Prompt style",    style="cyan",  no_wrap=True)
    table.add_column("System tokens",  justify="right")
    table.add_column("Output tokens",  justify="right")
    table.add_column("Total tokens",   justify="right")
    table.add_column("Est. cost (USD)", justify="right", style="green")

    for label, system_prompt in PROMPTS.items():
        # Count input tokens (system + user message)
        system_tokens = count_tokens(system_prompt)
        user_tokens   = count_tokens(USER_MESSAGE)
        input_tokens  = system_tokens + user_tokens

        # Make the actual API call
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=128,
            system=system_prompt,
            messages=[{"role": "user", "content": USER_MESSAGE}]
        )
        output_tokens = response.usage.output_tokens
        total_tokens  = input_tokens + output_tokens
        cost          = estimate_cost(input_tokens, output_tokens)

        table.add_row(
            label,
            str(system_tokens),
            str(output_tokens),
            str(total_tokens),
            f"${cost:.6f}",
        )

    console.print(table)


# ─────────────────────────────────────────────
#  Demo: scale cost to production volume
# ─────────────────────────────────────────────
def estimate_production_cost(
    daily_requests: int,
    avg_input_tokens: int,
    avg_output_tokens: int,
    model: str = "claude-haiku-4-5-20251001"
) -> None:
    """
    Prints a monthly cost estimate for a given request volume.
    Useful for budgeting before you launch a product.
    """
    cost_per_request = estimate_cost(avg_input_tokens, avg_output_tokens, model)
    monthly_cost     = cost_per_request * daily_requests * 30

    console.print(f"\n[bold]Production cost estimate:[/bold]")
    console.print(f"  Model:              {model}")
    console.print(f"  Daily requests:     {daily_requests:,}")
    console.print(f"  Avg input tokens:   {avg_input_tokens:,}")
    console.print(f"  Avg output tokens:  {avg_output_tokens:,}")
    console.print(f"  Cost per request:   ${cost_per_request:.6f}")
    console.print(f"  [green]Monthly estimate:   ${monthly_cost:,.2f}[/green]")


if __name__ == "__main__":
    console.print("\n[bold]Module 1, Lesson 2: Token Economics[/bold]\n")

    console.print("[bold cyan]Demo 1: System prompt length vs cost[/bold cyan]")
    run_token_comparison()

    console.print("\n[bold cyan]Demo 2: Production volume estimation[/bold cyan]")
    # Simulate a support bot with 1 000 requests/day
    estimate_production_cost(
        daily_requests=1_000,
        avg_input_tokens=500,
        avg_output_tokens=150,
    )

    console.print("\n[bold green]✓ Lesson 2 complete![/bold green]")
    console.print("Next: [italic]python code/module1/lesson3_principles.py[/italic]\n")
