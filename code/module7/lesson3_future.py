"""
Module 7, Lesson 3: Emerging Patterns in Context Engineering
=============================================================
Three patterns that extend beyond the CWA layers covered so far:
  1. Self-reflection  — model reviews and improves its own output
  2. Constitutional   — model checks its answer against explicit principles
  3. Meta-prompting   — model generates a better system prompt than you wrote

Run:
    python code/module7/lesson3_future.py
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


def llm(prompt: str, system: str = "You are a helpful assistant.") -> str:
    r = client.messages.create(
        model=MODEL_FAST, max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text.strip()


# ════════════════════════════════════════════════════════════════════════
#  PATTERN 1: Self-Reflection
#  Generate → critique own answer → improve → return polished version
# ════════════════════════════════════════════════════════════════════════
def self_reflect(task: str, iterations: int = 2) -> str:
    """Generate an answer, then iteratively critique and improve it."""
    answer = llm(task)
    console.print(Panel(answer, title="[dim]Initial draft[/dim]", border_style="dim"))

    for i in range(iterations):
        critique = llm(
            f"Task: {task}\n\nDraft answer:\n{answer}\n\n"
            "List 2 specific improvements you could make (clarity, completeness, accuracy):",
            system="You are a critical reviewer. Be specific about what is weak.",
        )
        console.print(f"  [dim]Critique {i+1}:[/dim] {critique[:120]}...")

        answer = llm(
            f"Task: {task}\n\nPrevious answer:\n{answer}\n\nCritique:\n{critique}\n\n"
            "Write an improved version that addresses the critique:",
            system="Improve the answer based on the critique. Keep it concise.",
        )

    return answer


# ════════════════════════════════════════════════════════════════════════
#  PATTERN 2: Constitutional Checking
#  Generate → check against explicit principles → revise if violated
# ════════════════════════════════════════════════════════════════════════
CONSTITUTION = """
1. Every claim must be verifiable or clearly marked as an estimate.
2. Never recommend a single solution — always present trade-offs.
3. Use plain English — no jargon without explanation.
4. Be honest about uncertainty; use 'typically' or 'often' not 'always'.
"""


def constitutional_check(answer: str, task: str) -> tuple[str, bool]:
    """Returns (violations_or_ok, all_passed)."""
    verdict = llm(
        f"Principles:\n{CONSTITUTION}\n\n"
        f"Task: {task}\nAnswer: {answer}\n\n"
        "Does the answer violate any principle? Reply 'PASS' if all are met, "
        "or list the specific violations.",
        system="You are a strict compliance checker. Be precise.",
    )
    passed = verdict.strip().upper().startswith("PASS")
    return verdict, passed


def constitutional_answer(task: str) -> str:
    """Generates and revises until all constitutional principles are met."""
    answer = llm(task)

    for attempt in range(3):
        verdict, passed = constitutional_check(answer, task)
        if passed:
            console.print(f"  [green]✓ Passed constitutional check (attempt {attempt+1})[/green]")
            return answer

        console.print(f"  [yellow]✗ Violations found (attempt {attempt+1}): {verdict[:100]}...[/yellow]")
        answer = llm(
            f"Task: {task}\n\nDraft:\n{answer}\n\nViolations to fix:\n{verdict}\n\n"
            "Revise the answer to comply with all principles:",
        )

    return answer


# ════════════════════════════════════════════════════════════════════════
#  PATTERN 3: Meta-Prompting
#  Use the model to generate a better system prompt than you wrote
# ════════════════════════════════════════════════════════════════════════
def meta_prompt(goal: str, weak_system_prompt: str) -> str:
    """Ask the model to rewrite a weak system prompt into an expert one."""
    return llm(
        f"Goal: {goal}\n\n"
        f"Current system prompt (weak):\n{weak_system_prompt}\n\n"
        "Rewrite this as an expert-level system prompt that will produce better results. "
        "Include: clear role, constraints, output format, and edge case handling.",
        system=(
            "You are a prompt engineer. Write system prompts that are specific, "
            "constraint-rich, and format-explicit. Never be vague."
        ),
    )


if __name__ == "__main__":
    console.print("\n[bold]Module 7, Lesson 3 — Emerging Patterns[/bold]\n")

    # ── Pattern 1: Self-Reflection ─────────────────────────────────────
    console.print(Rule("[bold]Pattern 1: Self-Reflection[/bold]"))
    task = "Explain why RAG is better than fine-tuning for keeping AI answers up to date."
    console.print(f"[yellow]Task:[/yellow] {task}\n")
    final = self_reflect(task, iterations=1)
    console.print(Panel(final, title="[green]After self-reflection[/green]"))

    # ── Pattern 2: Constitutional Checking ────────────────────────────
    console.print(Rule("[bold]Pattern 2: Constitutional Checking[/bold]"))
    console.print(f"[dim]Constitution:{CONSTITUTION}[/dim]")
    task = "What database should I use for my new app?"
    console.print(f"[yellow]Task:[/yellow] {task}\n")
    answer = constitutional_answer(task)
    console.print(Panel(answer, title="[green]Constitution-compliant answer[/green]"))

    # ── Pattern 3: Meta-Prompting ─────────────────────────────────────
    console.print(Rule("[bold]Pattern 3: Meta-Prompting[/bold]"))
    goal = "A customer support bot for a SaaS product that resolves issues on the first contact"
    weak = "You are a helpful customer support agent. Help customers with their issues."
    console.print(f"[yellow]Goal:[/yellow] {goal}")
    console.print(Panel(weak, title="Weak system prompt (before)", border_style="dim"))
    improved = meta_prompt(goal, weak)
    console.print(Panel(improved, title="[green]Improved system prompt (after)[/green]"))

    console.print("\n[bold green]✓ Lesson 3 complete![/bold green]")
    console.print("Next: [italic]python code/module7/lesson4_cwa.py[/italic]\n")
