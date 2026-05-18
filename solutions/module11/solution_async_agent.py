"""
SOLUTION: Module 11 — Async Research Assistant
===============================================
A fully async version of the final project's research assistant.
Concurrent RAG retrieval + parallel evaluation + async streaming.

Run:
    python solutions/module11/solution_async_agent.py
"""

import os
import sys
import asyncio
import anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST, MODEL_QUALITY

load_dotenv()
console      = Console()
async_client = anthropic.AsyncAnthropic()

TOPICS = [
    "What is Direct Air Capture and how much does it cost?",
    "How does ocean acidification affect coral reefs?",
    "What percentage of global electricity comes from renewables?",
]

KNOWLEDGE = [
    "DAC technology removes CO2 from air at $300-600/tonne, projected to fall to $100-200 by 2030.",
    "Ocean pH dropped from 8.2 to 8.1 (26% more acidic). At 2°C, coral reefs face long-term degradation.",
    "Global renewables reached 3,372 GW in 2023. Solar PV cost fell 89% since 2010.",
]


async def answer_topic(topic: str, context: str) -> str:
    """Answers one topic concurrently with others."""
    response = await async_client.messages.create(
        model=MODEL_FAST,
        max_tokens=256,
        system="You are a climate science researcher. Answer concisely using only the provided context.",
        messages=[{"role": "user", "content": f"Context: {context}\n\nQuestion: {topic}"}],
    )
    return response.content[0].text.strip()


async def score_answer(answer: str, context: str) -> float:
    response = await async_client.messages.create(
        model=MODEL_FAST, max_tokens=10,
        messages=[{"role": "user", "content":
            f"Context: {context}\nAnswer: {answer}\n"
            "Rate faithfulness 0.0-1.0. Reply with ONLY a decimal."
        }]
    )
    try:
        return float(response.content[0].text.strip())
    except ValueError:
        return 0.0


async def main():
    console.print(Panel(
        "[bold]Async Research Assistant[/bold]\n"
        "All queries answered and scored in parallel",
        title="Solution: Module 11",
        border_style="blue",
    ))

    import time
    start = time.perf_counter()

    # ── Answer all topics in parallel ────────────────────────────────────
    console.print(f"\n[dim]Answering {len(TOPICS)} topics concurrently...[/dim]")
    answers = await asyncio.gather(*[
        answer_topic(topic, ctx)
        for topic, ctx in zip(TOPICS, KNOWLEDGE)
    ])

    # ── Score all answers in parallel ─────────────────────────────────────
    console.print("[dim]Scoring all answers concurrently...[/dim]")
    scores = await asyncio.gather(*[
        score_answer(answer, ctx)
        for answer, ctx in zip(answers, KNOWLEDGE)
    ])

    elapsed = time.perf_counter() - start
    console.print(f"[green]✓ Completed in {elapsed:.2f}s (all parallel)[/green]\n")

    # ── Display results ───────────────────────────────────────────────────
    for topic, answer, score in zip(TOPICS, answers, scores):
        color = "green" if score >= 0.8 else "yellow" if score >= 0.5 else "red"
        console.print(Rule(f"[dim]{topic[:60]}[/dim]"))
        console.print(Panel(answer, title=f"Answer | Faith: [{color}]{score:.2f}[/{color}]"))

    avg = sum(scores) / len(scores)
    console.print(f"\n[bold]Average faithfulness: [green]{avg:.2f}[/green][/bold]")
    console.print("\n[bold green]✓ Solution complete![/bold green]\n")


if __name__ == "__main__":
    asyncio.run(main())
