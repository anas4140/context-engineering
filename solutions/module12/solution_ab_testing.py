"""
SOLUTION: Module 12 — Full A/B Testing Pipeline
================================================
Complete prompt A/B testing workflow:
  - PromptRegistry tracks all versions
  - A/B test measures quality delta
  - Promotion gated on win rate threshold

Run:
    python solutions/module12/solution_ab_testing.py
"""

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
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


@dataclass
class PromptVersion:
    name: str; version: str; system: str
    notes: str = ""; production: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


class PromptRegistry:
    def __init__(self): self._store: dict = {}
    def register(self, p): self._store.setdefault(p.name, []).append(p); return self
    def get(self, name, version): return next((p for p in self._store.get(name,[]) if p.version==version), None)
    def get_production(self, name): return next((p for p in reversed(self._store.get(name,[])) if p.production), None)
    def history(self, name): return self._store.get(name, [])
    def promote(self, name, version):
        for p in self._store.get(name, []): p.production = (p.version == version)


def generate(system: str, question: str, context: str) -> str:
    r = client.messages.create(model=MODEL_FAST, max_tokens=200, system=system,
        messages=[{"role":"user","content":f"Context: {context}\n\nQuestion: {question}"}])
    return r.content[0].text.strip()


def judge_pair(a: str, b: str, question: str, context: str) -> str:
    v = client.messages.create(model=MODEL_FAST, max_tokens=5,
        messages=[{"role":"user","content":(
            f"Q: {question}\nCtx: {context}\nA: {a}\nB: {b}\n"
            "Which is better? Reply A, B, or TIE only."
        )}]).content[0].text.strip().upper()
    for x in ["A","B","TIE"]:
        if x in v: return x
    return "TIE"


TEST_CASES = [
    {"question":"What is prompt caching?","context":"Prompt caching stores prompt prefixes server-side, cutting cost up to 90%."},
    {"question":"What is RAG?","context":"RAG retrieves documents and injects them into the prompt to ground answers in facts."},
    {"question":"What is the Batch API?","context":"The Batch API processes requests asynchronously at 50% lower cost."},
    {"question":"What is MCP?","context":"MCP (Model Context Protocol) is an open standard for AI tool discovery and invocation."},
    {"question":"What is extended thinking?","context":"Extended thinking gives Claude a private scratchpad for reasoning before answering."},
]


def ab_test(prompt_a: PromptVersion, prompt_b: PromptVersion, cases: list) -> dict:
    wins_a = wins_b = ties = 0
    for case in cases:
        a = generate(prompt_a.system, case["question"], case["context"])
        b = generate(prompt_b.system, case["question"], case["context"])
        winner = judge_pair(a, b, case["question"], case["context"])
        if winner == "A": wins_a += 1
        elif winner == "B": wins_b += 1
        else: ties += 1
        icon = {"A": "🔵", "B": "🟢", "TIE": "⬜"}[winner]
        console.print(f"  {icon} {case['question'][:45]} → {winner}")

    decisive  = wins_a + wins_b
    win_rate  = wins_b / decisive if decisive > 0 else 0.5
    winner_id = "B" if win_rate > 0.6 and decisive >= 3 else "A" if win_rate < 0.4 and decisive >= 3 else None
    return {"wins_a": wins_a, "wins_b": wins_b, "ties": ties, "win_rate_b": win_rate, "winner": winner_id}


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 12 — Full A/B Testing Pipeline[/bold]\n")

    registry = PromptRegistry()
    registry.register(PromptVersion("qa", "v1.0", "You are a helpful assistant. Answer clearly.", "Generic", production=True))
    registry.register(PromptVersion("qa", "v2.0",
        "You are a documentation specialist. Answer with: (1) direct answer, (2) example, (3) tip. "
        "Cite the context explicitly. Never fabricate.", "Structured + citation"))

    a = registry.get("qa", "v1.0")
    b = registry.get("qa", "v2.0")

    console.print(Panel(a.system, title=f"[blue]Prompt A — {a.version} (production)[/blue]"))
    console.print(Panel(b.system, title=f"[green]Prompt B — {b.version} (challenger)[/green]"))
    console.print(Rule("Running A/B test"))

    result = ab_test(a, b, TEST_CASES)

    console.print(Rule("Results"))
    console.print(
        f"[blue]A: {result['wins_a']}[/blue]  [green]B: {result['wins_b']}[/green]  "
        f"[dim]Ties: {result['ties']}[/dim]  |  B win rate: [bold]{result['win_rate_b']:.0%}[/bold]"
    )

    if result["winner"] == "B":
        registry.promote("qa", "v2.0")
        console.print("[green]✓ Promoted v2.0 to production[/green]")
    elif result["winner"] == "A":
        console.print("[red]✗ v2.0 rejected — v1.0 retained[/red]")
    else:
        console.print("[yellow]⚠ Inconclusive — extend the test set[/yellow]")

    prod = registry.get_production("qa")
    console.print(Panel(prod.system, title=f"[green]Production: {prod.version}[/green]"))
    console.print("\n[bold green]✓ Solution complete![/bold green]\n")
