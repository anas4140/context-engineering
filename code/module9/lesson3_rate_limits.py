"""
Module 9, Lesson 3: Rate Limits & Retry Logic
==============================================
Demonstrates production-grade error handling:
  1. Automatic retry with exponential back-off via tenacity
  2. Reading Retry-After headers for precise waits
  3. Token-aware request pacing within a TPM window

Run:
    python code/module9/lesson3_rate_limits.py
"""

import os
import sys
import time
import logging
import anthropic
from anthropic import Anthropic
from dotenv import load_dotenv
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log,
)
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
client  = Anthropic()
console = Console()
logger  = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)


# ─────────────────────────────────────────────
#  Pattern 1: Tenacity-based automatic retry
# ─────────────────────────────────────────────
@retry(
    retry=retry_if_exception_type((
        anthropic.RateLimitError,
        anthropic.APIConnectionError,
        anthropic.APITimeoutError,
    )),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(6),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def create_with_retry(**kwargs):
    """Drop-in replacement for client.messages.create() with automatic retries."""
    return client.messages.create(**kwargs)


# ─────────────────────────────────────────────
#  Pattern 2: Retry-After header awareness
# ─────────────────────────────────────────────
def create_header_aware(**kwargs):
    """Reads the Retry-After header for precise wait times on 429 responses."""
    while True:
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError as e:
            retry_after = int(getattr(e.response, "headers", {}).get("retry-after", 10))
            console.print(f"[yellow]Rate limited. Waiting {retry_after}s (from Retry-After header)...[/yellow]")
            time.sleep(retry_after)


# ─────────────────────────────────────────────
#  Pattern 3: Token-aware pacing
# ─────────────────────────────────────────────
class TokenPacer:
    """
    Paces requests so token usage stays within a TPM (tokens-per-minute) limit.
    Resets the usage counter at the start of each minute window.
    """

    def __init__(self, tpm_limit: int = 40_000):
        self.tpm_limit    = tpm_limit
        self.tokens_used  = 0
        self.window_start = time.time()

    def _maybe_reset(self):
        if time.time() - self.window_start >= 60:
            self.tokens_used  = 0
            self.window_start = time.time()

    def _estimate(self, text: str) -> int:
        return len(text) // 4  # ~4 chars per token for English

    def create(self, content: str, **kwargs):
        self._maybe_reset()
        estimated = self._estimate(content)
        if self.tokens_used + estimated > self.tpm_limit:
            wait = 60 - (time.time() - self.window_start)
            console.print(f"[dim]Approaching TPM limit — pacing: waiting {wait:.1f}s[/dim]")
            time.sleep(max(wait, 0))
            self._maybe_reset()

        response = client.messages.create(content=content, **kwargs)
        actual = response.usage.input_tokens + response.usage.output_tokens
        self.tokens_used += actual
        console.print(f"[dim]Tokens this window: {self.tokens_used}/{self.tpm_limit}[/dim]")
        return response


# ─────────────────────────────────────────────
#  Pattern 4: Read quota headers
# ─────────────────────────────────────────────
def show_quota_headers(response):
    """Logs remaining quota from response headers."""
    try:
        headers = response._raw_response.headers
        console.print(
            f"[dim]Quota — requests remaining: "
            f"{headers.get('anthropic-ratelimit-requests-remaining', 'n/a')} | "
            f"tokens remaining: "
            f"{headers.get('anthropic-ratelimit-tokens-remaining', 'n/a')}[/dim]"
        )
    except AttributeError:
        console.print("[dim]Headers not accessible in this context.[/dim]")


if __name__ == "__main__":
    console.print("\n[bold]Module 9, Lesson 3 — Rate Limits & Retry Logic[/bold]\n")

    # ── Demo 1: retrying call ────────────────────────────────────────────
    console.print(Rule("Pattern 1: Automatic retry (tenacity)"))
    console.print("[dim]Calling create_with_retry() — retries on 429/connection errors[/dim]")
    r1 = create_with_retry(
        model=MODEL_FAST, max_tokens=64,
        messages=[{"role": "user", "content": "Say 'retry works' and nothing else."}],
    )
    console.print(f"[green]Response:[/green] {r1.content[0].text}")

    # ── Demo 2: quota headers ────────────────────────────────────────────
    console.print(Rule("Pattern 4: Reading quota headers"))
    show_quota_headers(r1)

    # ── Demo 3: token pacing ─────────────────────────────────────────────
    console.print(Rule("Pattern 3: Token-aware pacing"))
    pacer   = TokenPacer(tpm_limit=40_000)
    queries = [
        "What is 5 + 5?",
        "Name a planet.",
        "What colour is the sky?",
    ]
    for q in queries:
        r = pacer.create(
            content=q,
            model=MODEL_FAST, max_tokens=32,
            messages=[{"role": "user", "content": q}],
        )
        console.print(f"  Q: {q}  →  A: {r.content[0].text.strip()}")

    console.print("\n[bold green]✓ Lesson 3 complete![/bold green]")
    console.print("Next: [italic]python code/module10/lesson1_mcp_client.py[/italic]\n")
