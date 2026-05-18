"""
Module 11, Lesson 2: Concurrent Multi-Agent Systems
=====================================================
Applies asyncio to the orchestrator-subagent pattern:
  - Parallel subagents run simultaneously instead of sequentially
  - Error handling with return_exceptions=True
  - Per-call timeouts with asyncio.wait_for
  - Async evaluation pipeline

Run:
    python code/module11/lesson2_concurrent_agents.py
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

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
console      = Console()
async_client = anthropic.AsyncAnthropic()


# ── Generic async subagent ───────────────────────────────────────────────
async def subagent(name: str, system: str, task: str, timeout: float = 30.0) -> str:
    """Single-purpose async agent with timeout."""
    try:
        response = await asyncio.wait_for(
            async_client.messages.create(
                model=MODEL_FAST, max_tokens=512,
                system=system,
                messages=[{"role": "user", "content": task}],
            ),
            timeout=timeout,
        )
        return response.content[0].text.strip()
    except asyncio.TimeoutError:
        return f"[{name} timed out after {timeout}s]"
    except Exception as e:
        return f"[{name} error: {e}]"


# ── Parallel research team ───────────────────────────────────────────────
async def parallel_research(topic: str) -> dict:
    """Three specialised researchers run concurrently."""
    console.print(f"  [dim]Launching 3 subagents in parallel for: {topic}[/dim]")
    start = time.perf_counter()

    facts, pros, cons = await asyncio.gather(
        subagent("Researcher", "List 3 key facts with numbers/dates where possible.", f"Facts about: {topic}"),
        subagent("Analyst",    "List 3 concrete benefits with examples.",             f"Benefits of: {topic}"),
        subagent("Risk analyst","List 3 risks or limitations with context.",          f"Risks of: {topic}"),
    )

    elapsed = time.perf_counter() - start
    console.print(f"  [dim]All 3 agents completed in {elapsed:.2f}s[/dim]")
    return {"facts": facts, "pros": pros, "cons": cons}


async def synthesise(topic: str, research: dict) -> str:
    """Synthesiser agent combines all research into a final answer."""
    research_text = "\n\n".join(f"**{k.title()}**:\n{v}" for k, v in research.items())
    return await subagent(
        "Synthesiser",
        "You are a technical writer. Synthesise research into a clear, balanced 2-paragraph summary.",
        f"Topic: {topic}\n\nResearch:\n{research_text}",
        timeout=60.0,
    )


# ── Parallel evaluation pipeline ─────────────────────────────────────────
async def score_metric(metric: str, answer: str, reference: str) -> float:
    prompts = {
        "faithfulness": f"Context: {reference}\nAnswer: {answer}\nRate faithfulness 0-1. Reply with only a decimal.",
        "relevance":    f"Question: {reference}\nAnswer: {answer}\nRate relevance 0-1. Reply with only a decimal.",
    }
    result = await subagent(metric, "Reply with ONLY a decimal number between 0.0 and 1.0.", prompts[metric])
    try:
        return float(result.strip())
    except ValueError:
        return 0.0


async def evaluate_parallel(answer: str, context: str, question: str) -> dict:
    """Runs all metrics concurrently — 1 roundtrip instead of N sequential."""
    start = time.perf_counter()
    faith, rel = await asyncio.gather(
        score_metric("faithfulness", answer, context),
        score_metric("relevance",    answer, question),
    )
    elapsed = time.perf_counter() - start
    return {"faithfulness": faith, "relevance": rel, "wall_time": round(elapsed, 2)}


# ── Error-tolerant gather ─────────────────────────────────────────────────
async def gather_with_fallbacks(tasks: list) -> list:
    """Runs tasks concurrently; failed tasks return None instead of crashing."""
    results = await asyncio.gather(*tasks, return_exceptions=True)
    safe    = []
    for i, r in enumerate(results):
        if isinstance(r, Exception):
            console.print(f"  [yellow]Task {i} failed: {r}[/yellow]")
            safe.append(None)
        else:
            safe.append(r)
    return safe


async def main():
    console.print("\n[bold]Module 11, Lesson 2 — Concurrent Multi-Agent Systems[/bold]\n")

    # ── Demo 1: Parallel research team ───────────────────────────────────
    console.print(Rule("Demo 1: Parallel research team (3 agents at once)"))
    topic    = "using large language models in production"
    research = await parallel_research(topic)

    for section, content in research.items():
        console.print(Panel(content[:300], title=f"[cyan]{section.title()}[/cyan]"))

    console.print("\n[dim]Synthesising...[/dim]")
    summary = await synthesise(topic, research)
    console.print(Panel(summary, title="[green]Final synthesis[/green]"))

    # ── Demo 2: Parallel evaluation ───────────────────────────────────────
    console.print(Rule("Demo 2: Parallel evaluation pipeline"))
    answer   = "RAG grounds LLM answers in retrieved facts, reducing hallucination."
    context  = "RAG (Retrieval-Augmented Generation) retrieves relevant documents and injects them into the prompt, ensuring the model's answer is grounded in provided facts."
    question = "What is RAG and why does it reduce hallucination?"

    scores = await evaluate_parallel(answer, context, question)
    console.print(
        f"Faithfulness: [green]{scores['faithfulness']:.2f}[/green] | "
        f"Relevance: [green]{scores['relevance']:.2f}[/green] | "
        f"Wall time: {scores['wall_time']}s"
    )

    # ── Demo 3: Error-tolerant gather ─────────────────────────────────────
    console.print(Rule("Demo 3: Error-tolerant gather"))
    tasks = [
        subagent("good",    "Answer concisely.", "What is 2+2?"),
        subagent("timeout", "Answer concisely.", "What is 3+3?", timeout=0.001),  # will timeout
        subagent("good2",   "Answer concisely.", "What is 4+4?"),
    ]
    results = await gather_with_fallbacks(tasks)
    for i, r in enumerate(results):
        status = f"[green]{r}[/green]" if r else "[red]Failed (graceful fallback)[/red]"
        console.print(f"  Task {i+1}: {status}")

    console.print("\n[bold green]✓ Lesson 2 complete![/bold green]")
    console.print("Next: [italic]python code/module12/lesson1_prompt_versioning.py[/italic]\n")


if __name__ == "__main__":
    asyncio.run(main())
