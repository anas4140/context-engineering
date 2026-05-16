"""
Module 7, Lesson 1: Emerging Patterns in Context Engineering
=============================================================
Demonstrates three modern patterns:
  1. Prompt caching — reduce cost on repeated long system prompts
  2. Structured outputs — get valid JSON from the model every time
  3. Extended thinking — let Claude reason before answering (shown conceptually)

Run:
    python code/module7/lesson1_patterns.py
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.rule import Rule

load_dotenv()
client  = Anthropic()
console = Console()
MODEL   = "claude-haiku-4-5-20251001"


# ─────────────────────────────────────────────
#  PATTERN 1: Prompt Caching
#  Mark large, stable system prompt blocks with
#  cache_control so they are cached server-side.
#  Subsequent requests with the same prefix are
#  dramatically cheaper and faster.
# ─────────────────────────────────────────────
# Simulate a large static knowledge block (a real use case would have thousands
# of tokens — product catalogues, legal docs, company policies, etc.)
LARGE_STATIC_KNOWLEDGE = "\n".join([
    f"Policy {i:03d}: " + ("ACME Inc. policy content. " * 20)
    for i in range(30)
])   # ~2,400 tokens — simulates a large static context block


def call_without_caching(user_query: str) -> dict:
    """Standard API call — system prompt processed fresh every time."""
    system = f"You are an HR assistant with access to these policies:\n\n{LARGE_STATIC_KNOWLEDGE}"
    response = client.messages.create(
        model=MODEL, max_tokens=128,
        system=system,
        messages=[{"role": "user", "content": user_query}]
    )
    return {
        "answer":        response.content[0].text,
        "input_tokens":  response.usage.input_tokens,
        "cache_read":    getattr(response.usage, "cache_read_input_tokens", 0),
        "cache_created": getattr(response.usage, "cache_creation_input_tokens", 0),
    }


def call_with_caching(user_query: str) -> dict:
    """
    Cache-enabled API call.
    The large knowledge block is marked with cache_control.
    After the first call, subsequent calls read from cache at ~10% of normal cost.
    """
    response = client.messages.create(
        model=MODEL, max_tokens=128,
        system=[
            {
                "type": "text",
                "text": "You are an HR assistant with access to these policies:\n\n",
            },
            {
                "type": "text",
                "text": LARGE_STATIC_KNOWLEDGE,
                # This tells Anthropic to cache this block after the first request
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": user_query}]
    )
    return {
        "answer":        response.content[0].text,
        "input_tokens":  response.usage.input_tokens,
        "cache_read":    getattr(response.usage, "cache_read_input_tokens", 0),
        "cache_created": getattr(response.usage, "cache_creation_input_tokens", 0),
    }


# ─────────────────────────────────────────────
#  PATTERN 2: Structured Outputs
#  Ask the model to return JSON and parse it.
#  More reliable than parsing free text.
# ─────────────────────────────────────────────
def extract_structured_data(text: str) -> dict:
    """
    Extracts structured information from unstructured text.
    Returns a validated Python dict, not free text.
    """
    system = (
        "You are a data extraction assistant. "
        "Always respond with ONLY a valid JSON object — no markdown, no preamble. "
        "If a field is missing from the text, use null."
    )
    schema_instruction = """Extract these fields and return as JSON:
{
  "company_name": string or null,
  "revenue_usd_millions": number or null,
  "growth_pct_yoy": number or null,
  "key_products": array of strings,
  "sentiment": "positive" | "negative" | "neutral"
}"""

    user = f"{schema_instruction}\n\nText to extract from:\n{text}"

    response = client.messages.create(
        model=MODEL, max_tokens=256,
        system=system,
        messages=[{"role": "user", "content": user}]
    )

    raw = response.content[0].text.strip()
    # Strip markdown code fences if model adds them anyway
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "raw": raw}


# ─────────────────────────────────────────────
#  PATTERN 3: Extended Thinking (conceptual demo)
#  Claude reasons before answering using a
#  separate thinking token budget.
#  Note: requires claude-sonnet-4-6 or opus.
# ─────────────────────────────────────────────
def extended_thinking_demo(problem: str) -> dict:
    """
    Uses extended thinking for a complex reasoning problem.
    The thinking tokens are separate from the response.

    Note: Extended thinking requires Sonnet 4 or Opus — not Haiku.
    This demo uses claude-sonnet-4-6.
    """
    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            thinking={
                "type":         "enabled",
                "budget_tokens": 2048,   # Tokens dedicated to internal reasoning
            },
            messages=[{"role": "user", "content": problem}]
        )
        thinking_text = ""
        answer_text   = ""
        thinking_tokens = 0

        for block in response.content:
            if block.type == "thinking":
                thinking_text   = block.thinking
                thinking_tokens = len(thinking_text.split())   # approx
            elif block.type == "text":
                answer_text = block.text

        return {
            "answer":          answer_text,
            "thinking_tokens": thinking_tokens,
            "thinking_preview": thinking_text[:300] + "..." if len(thinking_text) > 300 else thinking_text,
        }
    except Exception as e:
        return {
            "answer":          f"Extended thinking demo skipped: {e}",
            "thinking_tokens": 0,
            "thinking_preview": "",
        }


if __name__ == "__main__":
    console.print("\n[bold]Module 7, Lesson 1: Emerging Patterns[/bold]\n")

    # ── Pattern 1: Caching ─────────────────────
    console.print(Rule("Pattern 1: Prompt Caching"))

    query = "What are the main HR policies I should know about?"

    # First call — creates the cache
    console.print("[dim]Call 1 (cache creation)...[/dim]")
    r1 = call_with_caching(query)

    # Second call — reads from cache (cheaper)
    console.print("[dim]Call 2 (cache read)...[/dim]")
    r2 = call_with_caching(query)

    # No-cache baseline
    console.print("[dim]Baseline (no cache)...[/dim]")
    r0 = call_without_caching(query)

    table = Table(title="Caching Token Comparison")
    table.add_column("Call",          style="cyan")
    table.add_column("Input tokens",  justify="right")
    table.add_column("Cache created", justify="right")
    table.add_column("Cache read",    justify="right")

    table.add_row("No-cache baseline", str(r0["input_tokens"]), "-", "-")
    table.add_row("With cache (call 1)", str(r1["input_tokens"]),
                  str(r1["cache_created"]), str(r1["cache_read"]))
    table.add_row("With cache (call 2)", str(r2["input_tokens"]),
                  str(r2["cache_created"]), str(r2["cache_read"]))
    console.print(table)

    # ── Pattern 2: Structured outputs ─────────
    console.print(Rule("\nPattern 2: Structured Outputs"))

    sample_texts = [
        "TechCorp reported Q3 revenue of $245M, up 18% year-over-year, driven by strong sales of their CloudBase and DataSync products. Executives expressed optimism about Q4.",
        "RetailCo saw a difficult quarter with revenue declining to $89M, down 12% from last year. Their legacy StoreFront software continues to lose market share.",
    ]
    for text in sample_texts:
        extracted = extract_structured_data(text)
        console.print(Panel(
            json.dumps(extracted, indent=2),
            title=f"Extracted: {text[:60]}..."
        ))

    # ── Pattern 3: Extended thinking ──────────
    console.print(Rule("\nPattern 3: Extended Thinking"))

    hard_problem = (
        "A farmer has 17 sheep. All but 9 run away. "
        "He then buys twice as many sheep as he has left, "
        "then sells a third of his total flock. "
        "How many sheep does he have now?"
    )
    result = extended_thinking_demo(hard_problem)
    console.print(Panel(result["answer"], title="Answer"))
    if result["thinking_preview"]:
        console.print(Panel(result["thinking_preview"],
                            title=f"Thinking preview (~{result['thinking_tokens']} tokens)"))

    console.print("\n[bold green]✓ Module 7 Lesson 1 complete![/bold green]")
    console.print("Next: [italic]python code/module7/lesson4_cwa.py[/italic]\n")
