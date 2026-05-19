"""
Module 5, Lesson 3: Multi-Agent Systems
=========================================
Demonstrates the orchestrator-subagent pattern:
  - Orchestrator receives a complex task and breaks it into subtasks
  - Researcher subagent finds facts about a topic
  - Writer subagent synthesises those facts into a polished answer
  - Critic subagent reviews the draft and flags weaknesses

Each subagent is stateless — it gets a task, returns a result, done.

Run:
    python code/module5/lesson3_multi_agent.py
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


# ── Subagent: stateless, single-turn ─────────────────────────────────────
def run_subagent(role: str, system: str, task: str, max_tokens: int = 512) -> str:
    """A single-purpose agent: system prompt defines its role, task is the input."""
    response = client.messages.create(
        model=MODEL_FAST,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": task}],
    )
    console.print(f"  [dim]{role} complete ({response.usage.output_tokens} tokens)[/dim]")
    return response.content[0].text


# ── Subagent roles ────────────────────────────────────────────────────────
def researcher(topic: str) -> str:
    return run_subagent(
        role="Researcher",
        system=(
            "You are a research specialist. Given a topic, list 5 key facts "
            "with specific numbers or dates where possible. Be concise and factual."
        ),
        task=f"Research this topic and list 5 key facts: {topic}",
    )


def writer(topic: str, facts: str) -> str:
    return run_subagent(
        role="Writer",
        system=(
            "You are a technical writer. Given a topic and research facts, "
            "write a clear, structured 2-paragraph summary. Use Markdown."
        ),
        task=f"Topic: {topic}\n\nFacts to include:\n{facts}\n\nWrite a 2-paragraph summary.",
        max_tokens=768,
    )


def critic(draft: str) -> str:
    return run_subagent(
        role="Critic",
        system=(
            "You are a quality reviewer. Identify 2-3 specific weaknesses in the draft "
            "(missing context, unsupported claims, unclear language). Be constructive."
        ),
        task=f"Review this draft and identify 2-3 specific weaknesses:\n\n{draft}",
    )


def refine(draft: str, critique: str) -> str:
    return run_subagent(
        role="Refiner",
        system="You are a technical writer. Improve a draft based on critique.",
        task=f"Original draft:\n{draft}\n\nCritique:\n{critique}\n\nWrite an improved version.",
        max_tokens=768,
    )


# ── Orchestrator ──────────────────────────────────────────────────────────
def orchestrate(topic: str) -> str:
    """
    Orchestrator pattern:
    1. Researcher → gathers facts
    2. Writer     → drafts from facts
    3. Critic     → reviews draft
    4. Refiner    → improves based on critique
    """
    console.print(f"\n[bold yellow]Topic:[/bold yellow] {topic}\n")

    console.print(Rule("Step 1: Research"))
    facts = researcher(topic)
    console.print(Panel(facts, title="[cyan]Researcher output[/cyan]"))

    console.print(Rule("Step 2: Write"))
    draft = writer(topic, facts)
    console.print(Panel(draft, title="[cyan]Writer output[/cyan]"))

    console.print(Rule("Step 3: Critique"))
    critique = critic(draft)
    console.print(Panel(critique, title="[cyan]Critic output[/cyan]"))

    console.print(Rule("Step 4: Refine"))
    final = refine(draft, critique)
    console.print(Panel(final, title="[green]Final output[/green]"))

    return final


if __name__ == "__main__":
    console.print("\n[bold]Module 5, Lesson 3 — Multi-Agent Systems[/bold]")
    console.print("[dim]Pattern: Orchestrator → Researcher → Writer → Critic → Refiner[/dim]\n")

    topics = [
        "The environmental impact of large language models",
        "Retrieval-Augmented Generation in production systems",
    ]

    for topic in topics:
        orchestrate(topic)
        console.print("\n" + "─" * 60 + "\n")

    console.print("[bold green]✓ Lesson 3 complete![/bold green]")
    console.print("Next: [italic]python code/module5/lesson4_structured_outputs.py[/italic]\n")
