"""
Module 11, Lesson 1: Async Basics with AsyncAnthropic
======================================================
Demonstrates AsyncAnthropic — the drop-in async client:
  1. Basic async call
  2. Concurrent queries with asyncio.gather (measures speedup)
  3. Async streaming
  4. Rate-limit-safe batching with asyncio.Semaphore

Run:
    python code/module11/lesson1_async_basics.py
"""

import os
import sys
import time
import asyncio
import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
console      = Console()
async_client = anthropic.AsyncAnthropic()
sync_client  = anthropic.Anthropic()

QUERIES = [
    "What is 7 × 8?",
    "Name the largest planet in the solar system.",
    "What does HTTP stand for?",
    "In what year was Python created?",
    "What is the chemical symbol for gold?",
]


# ── Basic async call ─────────────────────────────────────────────────────
async def ask(prompt: str) -> str:
    response = await async_client.messages.create(
        model=MODEL_FAST,
        max_tokens=64,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ── Sequential (sync) baseline ───────────────────────────────────────────
def sequential_sync(queries: list[str]) -> tuple[list[str], float]:
    start   = time.perf_counter()
    results = []
    for q in queries:
        r = sync_client.messages.create(
            model=MODEL_FAST, max_tokens=64,
            messages=[{"role": "user", "content": q}],
        )
        results.append(r.content[0].text.strip())
    return results, time.perf_counter() - start


# ── Concurrent (async) ───────────────────────────────────────────────────
async def concurrent_async(queries: list[str]) -> tuple[list[str], float]:
    start   = time.perf_counter()
    results = await asyncio.gather(*[ask(q) for q in queries])
    return list(results), time.perf_counter() - start


# ── Async streaming ──────────────────────────────────────────────────────
async def stream_response(prompt: str):
    console.print(f"[yellow]Streaming:[/yellow] {prompt}")
    console.print("[green]", end="")
    async with async_client.messages.stream(
        model=MODEL_FAST,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:
            console.print(text, end="", markup=False)
    console.print("[/green]")
    console.print()


# ── Rate-limit-safe concurrency with Semaphore ───────────────────────────
async def ask_safe(prompt: str, sem: asyncio.Semaphore) -> str:
    async with sem:
        return await ask(prompt)


async def batched_async(queries: list[str], max_concurrency: int = 3) -> list[str]:
    sem     = asyncio.Semaphore(max_concurrency)
    results = await asyncio.gather(*[ask_safe(q, sem) for q in queries])
    return list(results)


async def main():
    console.print("\n[bold]Module 11, Lesson 1 — Async Basics[/bold]\n")

    # ── Demo 1: Sequential vs. Concurrent speedup ────────────────────────
    console.print(Rule("Demo 1: Sequential vs. Concurrent (5 queries)"))
    console.print("[dim]Running sequential (sync)...[/dim]")
    sync_results, sync_time = sequential_sync(QUERIES)

    console.print("[dim]Running concurrent (async)...[/dim]")
    async_results, async_time = await concurrent_async(QUERIES)

    table = Table(title="Sequential vs. Concurrent", show_lines=True)
    table.add_column("Query",   width=35)
    table.add_column("Answer",  width=30)
    for q, a in zip(QUERIES, async_results):
        table.add_row(q, a[:29])
    console.print(table)

    speedup = sync_time / async_time if async_time > 0 else 1.0
    console.print(
        f"\n[bold]Sync:[/bold] {sync_time:.2f}s  |  "
        f"[bold]Async:[/bold] {async_time:.2f}s  |  "
        f"[green]Speedup: {speedup:.1f}×[/green]"
    )

    # ── Demo 2: Async streaming ──────────────────────────────────────────
    console.print(Rule("Demo 2: Async streaming"))
    await stream_response("Explain prompt caching in exactly 3 bullet points.")

    # ── Demo 3: Rate-limit-safe batching ────────────────────────────────
    console.print(Rule("Demo 3: Rate-limit-safe batching (max 3 concurrent)"))
    big_batch = QUERIES * 2   # 10 queries
    console.print(f"[dim]Running {len(big_batch)} queries with max_concurrency=3...[/dim]")
    start   = time.perf_counter()
    results = await batched_async(big_batch, max_concurrency=3)
    elapsed = time.perf_counter() - start
    console.print(f"[green]✓ {len(results)} results in {elapsed:.2f}s[/green]")

    console.print("\n[bold green]✓ Lesson 1 complete![/bold green]")
    console.print("Next: [italic]python code/module11/lesson2_concurrent_agents.py[/italic]\n")


if __name__ == "__main__":
    asyncio.run(main())
