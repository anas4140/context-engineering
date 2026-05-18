"""
Module 12, Lesson 1: Prompt Versioning
========================================
Demonstrates a lightweight prompt registry:
  - Register multiple versions of a prompt
  - Retrieve by version tag
  - Mark one version as production
  - Detect quality change between versions using LLM-as-judge

Run:
    python code/module12/lesson1_prompt_versioning.py
"""

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
client  = Anthropic()
console = Console()


# ── Prompt registry ──────────────────────────────────────────────────────
@dataclass
class PromptVersion:
    name:       str
    version:    str
    system:     str
    notes:      str = ""
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    production: bool = False


class PromptRegistry:
    def __init__(self):
        self._store: dict[str, list[PromptVersion]] = {}

    def register(self, prompt: PromptVersion):
        self._store.setdefault(prompt.name, []).append(prompt)
        return self

    def get(self, name: str, version: str) -> Optional[PromptVersion]:
        return next((p for p in self._store.get(name, []) if p.version == version), None)

    def get_production(self, name: str) -> Optional[PromptVersion]:
        return next((p for p in reversed(self._store.get(name, [])) if p.production), None)

    def history(self, name: str) -> list[PromptVersion]:
        return self._store.get(name, [])

    def promote(self, name: str, version: str):
        """Mark a version as production; demote all others."""
        for p in self._store.get(name, []):
            p.production = (p.version == version)


# ── Evaluation helpers ───────────────────────────────────────────────────
def generate(system_prompt: str, question: str, context: str) -> str:
    r = client.messages.create(
        model=MODEL_FAST, max_tokens=256,
        system=system_prompt,
        messages=[{"role": "user", "content": f"Context: {context}\n\nQuestion: {question}"}],
    )
    return r.content[0].text.strip()


def score_faithfulness(answer: str, context: str) -> float:
    r = client.messages.create(
        model=MODEL_FAST, max_tokens=10,
        messages=[{"role": "user", "content":
            f"Context: {context}\nAnswer: {answer}\n"
            "Rate faithfulness 0.0-1.0. Reply with ONLY a decimal."
        }]
    )
    try:
        return float(r.content[0].text.strip())
    except ValueError:
        return 0.0


def eval_prompt(system: str, test_cases: list[dict]) -> float:
    """Average faithfulness score over all test cases."""
    scores = [
        score_faithfulness(generate(system, c["question"], c["context"]), c["context"])
        for c in test_cases
    ]
    return round(sum(scores) / len(scores), 3)


# ── Test cases ───────────────────────────────────────────────────────────
TEST_CASES = [
    {
        "question": "How many PTO days do employees receive?",
        "context":  "Full-time employees receive 20 PTO days per year.",
    },
    {
        "question": "Can I work from home?",
        "context":  "Remote work is allowed up to 3 days per week with manager approval.",
    },
    {
        "question": "How long is parental leave?",
        "context":  "Primary caregivers receive 16 weeks of paid parental leave.",
    },
]

# ── Three versions of the same summariser prompt ─────────────────────────
PROMPTS = [
    PromptVersion(
        name="hr_answerer", version="v1.0",
        system="You are a helpful HR assistant. Answer employee questions.",
        notes="Initial version — generic",
    ),
    PromptVersion(
        name="hr_answerer", version="v1.1",
        system=(
            "You are an HR policy specialist. Answer ONLY from the provided context. "
            "If the context does not contain the answer, say 'I don't have that information.'"
        ),
        notes="Added context-only constraint",
        production=True,
    ),
    PromptVersion(
        name="hr_answerer", version="v1.2",
        system=(
            "You are an HR policy specialist. Answer ONLY from the provided context. "
            "If the context does not contain the answer, say 'I don't have that information.' "
            "Always quote the relevant policy text in your answer."
        ),
        notes="Added quote requirement — testing if it helps faithfulness",
    ),
]


if __name__ == "__main__":
    console.print("\n[bold]Module 12, Lesson 1 — Prompt Versioning[/bold]\n")

    # ── Build registry ────────────────────────────────────────────────────
    registry = PromptRegistry()
    for p in PROMPTS:
        registry.register(p)

    # ── Show history ──────────────────────────────────────────────────────
    console.print(Rule("Version history"))
    table = Table(title="hr_answerer prompt history", show_lines=True)
    table.add_column("Version",    width=8)
    table.add_column("Production", justify="center", width=12)
    table.add_column("Notes",      width=45)
    table.add_column("Created",    width=12)
    for p in registry.history("hr_answerer"):
        prod = "[green]★ PROD[/green]" if p.production else ""
        table.add_row(p.version, prod, p.notes, p.created_at)
    console.print(table)

    # ── Eval all versions ─────────────────────────────────────────────────
    console.print(Rule("Quality scores across versions"))
    console.print("[dim]Running evaluations (3 test cases × 3 versions)...[/dim]\n")

    scores = {}
    for p in registry.history("hr_answerer"):
        score = eval_prompt(p.system, TEST_CASES)
        scores[p.version] = score
        prod_tag = " ★" if p.production else ""
        color    = "green" if score >= 0.8 else "yellow" if score >= 0.6 else "red"
        console.print(f"  {p.version}{prod_tag}: [{color}]{score:.3f}[/{color}]  — {p.notes}")

    # ── Promote best version ──────────────────────────────────────────────
    console.print(Rule("Promotion decision"))
    best_version = max(scores, key=scores.get)
    current_prod = registry.get_production("hr_answerer")
    current_score = scores.get(current_prod.version, 0) if current_prod else 0

    if scores[best_version] > current_score + 0.02:
        registry.promote("hr_answerer", best_version)
        console.print(f"[green]Promoted {best_version} (score {scores[best_version]:.3f} vs {current_score:.3f})[/green]")
    else:
        console.print(f"[dim]Current production ({current_prod.version}) retained — no significant improvement[/dim]")

    prod = registry.get_production("hr_answerer")
    console.print(Panel(prod.system, title=f"[green]Production prompt: {prod.version}[/green]"))

    console.print("\n[bold green]✓ Lesson 1 complete![/bold green]")
    console.print("Next: [italic]python code/module12/lesson2_ab_testing.py[/italic]\n")
