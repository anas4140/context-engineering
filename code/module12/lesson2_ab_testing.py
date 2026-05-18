"""
Module 12, Lesson 2: A/B Testing Prompts
==========================================
Runs a controlled A/B test between two system prompts:
  - Same test cases, same model, only system prompt differs
  - Scores each answer with LLM-as-judge
  - Reports winner with win/loss/tie breakdown
  - Generates a recommendation

Run:
    python code/module12/lesson2_ab_testing.py
"""

import os
import sys
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

# ── Two competing system prompts ─────────────────────────────────────────
PROMPT_A = (
    "You are a helpful assistant. Answer the user's question clearly."
)

PROMPT_B = (
    "You are an expert technical writer specialising in AI documentation. "
    "Answer questions with: (1) a direct one-sentence answer, (2) a concrete example, "
    "(3) one practical tip. Be concise. Never answer from memory alone — always reason step by step."
)

# ── 8 test cases — diverse question types ────────────────────────────────
TEST_CASES = [
    {"question": "What is prompt caching?",
     "context":  "Prompt caching stores processed prompt prefixes server-side, reducing cost up to 90%."},
    {"question": "When should I use the Batch API?",
     "context":  "The Batch API processes requests asynchronously at 50% lower cost, ideal for eval runs."},
    {"question": "What is RAG?",
     "context":  "RAG retrieves relevant documents and injects them into the LLM prompt to ground answers in facts."},
    {"question": "How do I reduce hallucinations?",
     "context":  "Grounding answers in retrieved context and using faithfulness checks reduces hallucination."},
    {"question": "What is a thinking budget?",
     "context":  "The thinking budget caps how many tokens Claude may use for its hidden reasoning scratchpad."},
    {"question": "What is the ReAct pattern?",
     "context":  "ReAct alternates between reasoning and acting (tool calls) in a loop until the task is done."},
    {"question": "What is BM25?",
     "context":  "BM25 is a sparse retrieval algorithm that scores documents by term frequency and inverse document frequency."},
    {"question": "What does MCP stand for?",
     "context":  "MCP stands for Model Context Protocol — an open standard for AI tool discovery and invocation."},
]


def generate(system: str, case: dict) -> str:
    r = client.messages.create(
        model=MODEL_FAST, max_tokens=256,
        system=system,
        messages=[{"role": "user", "content":
            f"Context: {case['context']}\n\nQuestion: {case['question']}"
        }],
    )
    return r.content[0].text.strip()


def judge(answer_a: str, answer_b: str, question: str, context: str) -> str:
    """LLM-as-judge: returns 'A', 'B', or 'TIE'."""
    verdict = client.messages.create(
        model=MODEL_FAST, max_tokens=10,
        messages=[{"role": "user", "content": (
            f"Question: {question}\nContext: {context}\n\n"
            f"Answer A: {answer_a}\n\nAnswer B: {answer_b}\n\n"
            "Which answer is better (more accurate, clearer, more useful)? "
            "Reply with ONLY: A, B, or TIE"
        )}],
    ).content[0].text.strip().upper()
    for v in ["A", "B", "TIE"]:
        if v in verdict:
            return v
    return "TIE"


def run_ab_test(prompt_a: str, prompt_b: str, test_cases: list[dict]) -> dict:
    results = []
    console.print(f"[dim]Running {len(test_cases)} comparisons...[/dim]\n")

    for i, case in enumerate(test_cases, 1):
        answer_a = generate(prompt_a, case)
        answer_b = generate(prompt_b, case)
        winner   = judge(answer_a, answer_b, case["question"], case["context"])
        results.append({"case": case, "answer_a": answer_a, "answer_b": answer_b, "winner": winner})
        icon = {"A": "🔵", "B": "🟢", "TIE": "⬜"}.get(winner, "?")
        console.print(f"  {icon} Case {i}: {case['question'][:50]} → [bold]{winner}[/bold]")

    wins_a = sum(1 for r in results if r["winner"] == "A")
    wins_b = sum(1 for r in results if r["winner"] == "B")
    ties   = sum(1 for r in results if r["winner"] == "TIE")
    total_decisive = wins_a + wins_b

    win_rate_b = wins_b / total_decisive if total_decisive > 0 else 0.5

    # Recommendation: win_rate > 0.6 with ≥ 5 decisive comparisons
    if win_rate_b > 0.6 and total_decisive >= 5:
        recommendation = "Promote Prompt B to production"
        rec_color      = "green"
    elif win_rate_b < 0.4 and total_decisive >= 5:
        recommendation = "Keep Prompt A — Prompt B is worse"
        rec_color      = "red"
    else:
        recommendation = "Inconclusive — extend the test set"
        rec_color      = "yellow"

    return {
        "wins_a": wins_a, "wins_b": wins_b, "ties": ties,
        "win_rate_b": win_rate_b, "recommendation": recommendation,
        "rec_color": rec_color, "results": results,
    }


if __name__ == "__main__":
    console.print("\n[bold]Module 12, Lesson 2 — A/B Testing Prompts[/bold]\n")

    console.print(Panel(PROMPT_A, title="Prompt A (control)", border_style="blue"))
    console.print(Panel(PROMPT_B, title="Prompt B (challenger)", border_style="green"))
    console.print()

    report = run_ab_test(PROMPT_A, PROMPT_B, TEST_CASES)

    # ── Results table ─────────────────────────────────────────────────────
    console.print(Rule("Results"))
    table = Table(title="A/B Test Results", show_lines=True)
    table.add_column("Question",   width=40)
    table.add_column("Winner",     justify="center", width=8)
    for r in report["results"]:
        color = {"A": "blue", "B": "green", "TIE": "dim"}.get(r["winner"], "white")
        table.add_row(r["case"]["question"][:39], f"[{color}]{r['winner']}[/{color}]")
    console.print(table)

    # ── Summary ───────────────────────────────────────────────────────────
    console.print(Rule("Summary"))
    console.print(
        f"[blue]A wins:[/blue] {report['wins_a']}  |  "
        f"[green]B wins:[/green] {report['wins_b']}  |  "
        f"[dim]Ties:[/dim] {report['ties']}\n"
        f"B win rate: [bold]{report['win_rate_b']:.0%}[/bold]"
    )
    console.print(Panel(
        report["recommendation"],
        title="Recommendation",
        border_style=report["rec_color"],
    ))

    console.print("\n[bold green]✓ Lesson 2 complete![/bold green]\n")
