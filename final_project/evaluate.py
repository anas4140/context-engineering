"""
Final Project: Automated Evaluation Suite
==========================================
Runs 5 test queries against the Research Assistant and scores each
response on faithfulness, answer relevance, and context precision.

Flags any response with faithfulness < 0.7 — the primary hallucination signal.

Run:
    python final_project/evaluate.py
"""

import os
import sys
import json

# Allow imports from repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.rule import Rule
import chromadb
from chromadb.utils import embedding_functions

from config import MODEL_FAST, MODEL_QUALITY

load_dotenv()
client  = Anthropic()
console = Console()

# ── Import the assistant's components ────────
from final_project.research_assistant import (
    RESEARCH_DOCUMENTS,
    build_knowledge_base,
    retrieve,
    build_system_prompt,
    TOOLS,
    execute_tool,
)

FAITHFULNESS_THRESHOLD = 0.7

# ─────────────────────────────────────────────
#  TEST QUERIES
#  Add your own domain queries here for Deliverable 5.
#  Each entry: (question, expected_keywords)
#  expected_keywords: strings that SHOULD appear in a correct answer
# ─────────────────────────────────────────────
TEST_QUERIES = [
    (
        "What are the current costs of Direct Air Capture technology?",
        ["300", "600", "tonne", "DAC"],
    ),
    (
        "How does ocean acidification affect coral reefs?",
        ["coral", "pH", "acidif"],
    ),
    (
        "What percentage of global electricity comes from renewables?",
        ["30", "renewable", "solar"],
    ),
    (
        "What is BECCS and what are its limitations?",
        ["BECCS", "bioenergy", "land"],
    ),
    (
        "What is the capital of Mars?",   # Out-of-scope — should trigger fallback
        ["don't have", "not found", "provided documents", "I don't"],
    ),
]


# ─────────────────────────────────────────────
#  EVALUATION FUNCTIONS
# ─────────────────────────────────────────────
def score(metric: str, answer: str, reference: str) -> float:
    """
    Generic LLM-as-judge scorer.
    metric: 'faithfulness' | 'relevance' | 'precision'
    reference: context (for faithfulness/precision) or question (for relevance)
    """
    prompts = {
        "faithfulness": (
            f"Context: {reference}\nAnswer: {answer}\n"
            "Rate faithfulness 0.0-1.0: does every claim in the answer come from the context? "
            "Reply with ONLY a decimal number."
        ),
        "relevance": (
            f"Question: {reference}\nAnswer: {answer}\n"
            "Rate answer relevance 0.0-1.0: does the answer address the question? "
            "Reply with ONLY a decimal number."
        ),
        "precision": (
            f"Question: {answer}\nContext: {reference}\n"
            "Rate context precision 0.0-1.0: how relevant is the context to the question? "
            "Reply with ONLY a decimal number."
        ),
    }
    r = client.messages.create(
        model=MODEL_FAST, max_tokens=10,
        messages=[{"role": "user", "content": prompts[metric]}]
    )
    try:
        return round(float(r.content[0].text.strip()), 2)
    except ValueError:
        return 0.0


def run_assistant_query(query: str, collection) -> tuple[str, list[dict]]:
    """Runs a single query through the full assistant pipeline and returns (answer, chunks)."""
    chunks   = retrieve(query, collection, top_k=2)
    system   = build_system_prompt(chunks)
    messages = [{"role": "user", "content": query}]
    turns    = 0

    while turns < 8:
        turns += 1
        response = client.messages.create(
            model=MODEL_QUALITY, max_tokens=512,
            system=system, tools=TOOLS, messages=messages,
        )
        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text, chunks
            return "", chunks

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})

    return "Evaluation timeout.", chunks


def keyword_check(answer: str, keywords: list[str]) -> bool:
    """Returns True if at least one keyword appears in the answer (case-insensitive)."""
    answer_lower = answer.lower()
    return any(kw.lower() in answer_lower for kw in keywords)


# ─────────────────────────────────────────────
#  MAIN EVALUATION RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    console.print("\n[bold]Final Project: Automated Evaluation Suite[/bold]\n")

    console.print("[dim]Loading knowledge base...[/dim]")
    collection = build_knowledge_base()
    console.print("[green]✓ Knowledge base ready[/green]\n")

    table = Table(title="Evaluation Results", show_lines=True)
    table.add_column("Query (truncated)",     width=35)
    table.add_column("Faithfulness",          justify="right")
    table.add_column("Relevance",             justify="right")
    table.add_column("Ctx Precision",         justify="right")
    table.add_column("Keywords",              justify="center")
    table.add_column("Flag",                  justify="center")

    total_f = total_r = total_p = 0.0
    flagged = []

    for i, (query, expected_keywords) in enumerate(TEST_QUERIES, 1):
        console.print(f"[dim]Running query {i}/{len(TEST_QUERIES)}: {query[:60]}...[/dim]")

        answer, chunks = run_assistant_query(query, collection)
        context_text   = " ".join(c["content"] for c in chunks)

        f = score("faithfulness", answer, context_text)
        r = score("relevance",    answer, query)
        p = score("precision",    context_text, query)

        kw_ok    = keyword_check(answer, expected_keywords)
        low_faith = f < FAITHFULNESS_THRESHOLD

        if low_faith:
            flagged.append(query[:50])

        total_f += f
        total_r += r
        total_p += p

        f_str  = f"[red]{f:.2f}[/red]" if low_faith else f"[green]{f:.2f}[/green]"
        kw_str = "[green]✓[/green]" if kw_ok else "[red]✗[/red]"
        flag   = "[red]⚠ LOW[/red]" if low_faith else "[green]OK[/green]"

        table.add_row(
            query[:34] + "…" if len(query) > 34 else query,
            f_str, f"{r:.2f}", f"{p:.2f}", kw_str, flag,
        )

    n = len(TEST_QUERIES)
    table.add_section()
    table.add_row(
        "[bold]Averages[/bold]",
        f"[bold]{total_f/n:.2f}[/bold]",
        f"[bold]{total_r/n:.2f}[/bold]",
        f"[bold]{total_p/n:.2f}[/bold]",
        "", "",
    )

    console.print(table)

    if flagged:
        console.print(f"\n[red]⚠ {len(flagged)} response(s) flagged (faithfulness < {FAITHFULNESS_THRESHOLD}):[/red]")
        for q in flagged:
            console.print(f"  • {q}…")
        console.print(
            "\n[bold]Suggested fix:[/bold] Strengthen the Layer 2 safety rules and "
            "ensure the generator prompt says 'answer ONLY from the retrieved context'.\n"
        )
    else:
        console.print(f"\n[bold green]✓ All {n} queries passed the faithfulness threshold.[/bold green]\n")

    console.print("[bold green]✓ Evaluation complete![/bold green]\n")
