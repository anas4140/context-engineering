"""
Module 3, Lesson 4: Production RAG Patterns
============================================
Three patterns that fix the silent failure modes of basic RAG:
  1. Corrective RAG  — grade retrieved chunks; fall back to web search if irrelevant
  2. Self-RAG        — generator checks its own answer against context before returning
  3. Query routing   — classify the query and route to the right retriever

Run:
    python code/module3/lesson4_production_rag.py
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

# ── Tiny in-memory knowledge base ───────────────────────────────────────
DOCS = [
    {"id": "d1", "topic": "rag",       "content": "RAG combines retrieval with generation. Retrieved chunks ground the answer in facts."},
    {"id": "d2", "topic": "caching",   "content": "Prompt caching stores processed prompt prefixes server-side, reducing cost by up to 90%."},
    {"id": "d3", "topic": "agents",    "content": "Agents use tools in a ReAct loop: Reason → Act → Observe → repeat until done."},
    {"id": "d4", "topic": "chunking",  "content": "Fixed-size chunks overlap by 10-20% to avoid splitting context across chunk boundaries."},
    {"id": "d5", "topic": "tokens",    "content": "Tokens are the basic unit of LLM processing. English text averages ~4 characters per token."},
]


def simple_retrieve(query: str, top_k: int = 2) -> list[dict]:
    """Keyword-based retrieval — no embeddings needed for this demo."""
    scored = []
    for doc in DOCS:
        score = sum(1 for word in query.lower().split() if word in doc["content"].lower())
        scored.append((score, doc))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored[:top_k] if score > 0]


def llm(prompt: str, system: str = "You are a helpful assistant.") -> str:
    r = client.messages.create(
        model=MODEL_FAST, max_tokens=256,
        system=system,
        messages=[{"role": "user", "content": prompt}],
    )
    return r.content[0].text.strip()


# ════════════════════════════════════════════════════════════════════════
#  PATTERN 1: Corrective RAG
#  Retrieve → grade relevance → fallback to web search if poor → generate
# ════════════════════════════════════════════════════════════════════════
def grade_relevance(chunk: str, query: str) -> bool:
    """Ask the LLM if this chunk is relevant to the query (yes/no)."""
    verdict = llm(
        f"Query: {query}\nChunk: {chunk}\n\nIs this chunk relevant? Reply YES or NO only.",
        system="You are a document relevance grader. Be strict."
    )
    return verdict.strip().upper().startswith("YES")


def corrective_rag(query: str) -> str:
    """Corrective RAG: grade each chunk; use web-search fallback if all fail."""
    chunks = simple_retrieve(query, top_k=3)

    # Grade each chunk
    relevant = [c for c in chunks if grade_relevance(c["content"], query)]
    console.print(f"  [dim]Retrieved: {len(chunks)} | Relevant after grading: {len(relevant)}[/dim]")

    if relevant:
        context = "\n".join(c["content"] for c in relevant)
    else:
        # Fallback: simulate web search result
        console.print("  [yellow]No relevant chunks — using web search fallback[/yellow]")
        context = f"[Web search result for '{query}']: General information retrieved from the web."

    return llm(
        f"Context:\n{context}\n\nQuestion: {query}\nAnswer concisely using only the context.",
        system="Answer only from the provided context. If unsure, say so.",
    )


# ════════════════════════════════════════════════════════════════════════
#  PATTERN 2: Self-RAG
#  Generate → check if answer is supported by context → regenerate if not
# ════════════════════════════════════════════════════════════════════════
def self_rag(query: str, max_retries: int = 2) -> str:
    """Self-RAG: generator critiques its own answer for faithfulness."""
    chunks   = simple_retrieve(query)
    context  = "\n".join(c["content"] for c in chunks) if chunks else "No relevant context found."
    system   = "Answer concisely. Use only the provided context."

    for attempt in range(1, max_retries + 2):
        answer = llm(f"Context:\n{context}\n\nQuestion: {query}", system=system)

        # Self-check: is the answer supported by the context?
        verdict = llm(
            f"Context: {context}\nAnswer: {answer}\n\n"
            "Is every claim in the answer directly supported by the context? Reply SUPPORTED or UNSUPPORTED.",
            system="You are a faithfulness checker. Be strict.",
        )
        supported = verdict.strip().upper().startswith("SUPPORTED")
        console.print(f"  [dim]Attempt {attempt}: {'✓ supported' if supported else '✗ unsupported — regenerating'}[/dim]")

        if supported or attempt > max_retries:
            return answer

        # Regenerate with stronger instruction
        system = "Answer ONLY from the context. Do not add any information not present in the context."

    return answer


# ════════════════════════════════════════════════════════════════════════
#  PATTERN 3: Query Routing
#  Classify query type → route to the right handler
# ════════════════════════════════════════════════════════════════════════
def classify_query(query: str) -> str:
    """Routes: 'factual' | 'calculation' | 'out_of_scope'"""
    verdict = llm(
        f"Classify this query into exactly one category: factual, calculation, out_of_scope.\n"
        f"Query: {query}\nReply with ONLY one word.",
        system="You are a query classifier. Reply with exactly one word: factual, calculation, or out_of_scope.",
    )
    category = verdict.strip().lower()
    for c in ["factual", "calculation", "out_of_scope"]:
        if c in category:
            return c
    return "factual"


def query_router(query: str) -> str:
    """Routes the query to the appropriate handler."""
    route = classify_query(query)
    console.print(f"  [dim]Route: {route}[/dim]")

    if route == "calculation":
        return llm(query, system="You are a calculator. Show your working.")

    if route == "out_of_scope":
        return "This question is outside the knowledge base. Please consult the documentation."

    # Default: factual RAG
    chunks  = simple_retrieve(query)
    context = "\n".join(c["content"] for c in chunks) if chunks else "No relevant context."
    return llm(f"Context:\n{context}\n\nQuestion: {query}", system="Answer from the context only.")


if __name__ == "__main__":
    console.print("\n[bold]Module 3, Lesson 4 — Production RAG Patterns[/bold]\n")

    test_cases = [
        ("What is prompt caching?",                   "factual — in knowledge base"),
        ("How do I bake a chocolate cake?",           "out of scope"),
        ("If I have 5 chunks each with 200 tokens, how many tokens total?", "calculation"),
    ]

    # ── Pattern 1: Corrective RAG ──────────────────────────────────────
    console.print(Rule("[bold]Pattern 1: Corrective RAG[/bold]"))
    for query, note in test_cases[:2]:
        console.print(f"\n[yellow]Q[/yellow] ({note}): {query}")
        answer = corrective_rag(query)
        console.print(Panel(answer, title="Corrective RAG"))

    # ── Pattern 2: Self-RAG ────────────────────────────────────────────
    console.print(Rule("[bold]Pattern 2: Self-RAG[/bold]"))
    query = "How does chunking overlap work?"
    console.print(f"\n[yellow]Q:[/yellow] {query}")
    answer = self_rag(query)
    console.print(Panel(answer, title="Self-RAG answer"))

    # ── Pattern 3: Query routing ───────────────────────────────────────
    console.print(Rule("[bold]Pattern 3: Query Routing[/bold]"))
    for query, note in test_cases:
        console.print(f"\n[yellow]Q[/yellow] ({note}): {query}")
        answer = query_router(query)
        console.print(Panel(answer, title="Routed answer"))

    console.print("\n[bold green]✓ Lesson 4 complete![/bold green]")
    console.print("Next: [italic]python code/module4/lesson1_anatomy.py[/italic]\n")
