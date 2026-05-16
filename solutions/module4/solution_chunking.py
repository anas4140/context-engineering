"""
SOLUTION: Module 4 — Chunking Strategy Comparison
===================================================
Answer key for the Module 4 Lesson 2 task:
Compare chunking strategies and find the optimal chunk size
for a given document and query type.

Run:
    python solutions/module4/solution_chunking.py
"""

import re
import tiktoken
import chromadb
from chromadb.utils import embedding_functions
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()
client  = Anthropic()
console = Console()
enc     = tiktoken.get_encoding("cl100k_base")

SAMPLE_DOCUMENT = """
ACME Inc. Employee Handbook — Section 3: Time Off and Leave Policies

3.1 Paid Time Off (PTO)
All full-time employees receive 20 days of Paid Time Off per year. PTO accrues
at a rate of 1.67 days per month starting from the first day of employment.
Unused PTO may be rolled over to the next year up to a maximum of 10 days.
Employees must request PTO at least 48 hours in advance through the HR portal.

3.2 Sick Leave
Separate from PTO, employees receive 10 sick days per year. Sick days do not
accrue and do not roll over. A doctor's note is required for absences of 3 or
more consecutive days. Sick leave cannot be converted to PTO.

3.3 Parental Leave
Primary caregivers receive 16 weeks of fully paid parental leave. Secondary
caregivers receive 4 weeks of fully paid leave. Leave must be taken within 12
months of the child's birth or adoption. Employees must give 30 days' notice
where possible.

3.4 Public Holidays
ACME observes 11 federal public holidays. Employees required to work on a public
holiday receive time-and-a-half pay and an additional day of PTO. The holiday
schedule is published each January on the HR portal.

3.5 Bereavement Leave
Employees receive up to 5 days of paid bereavement leave for the death of an
immediate family member (spouse, child, parent, sibling). For extended family,
up to 3 days are provided. Additional unpaid leave may be requested.
"""

QUERIES = [
    "How many PTO days do I get and can I roll them over?",
    "What is the parental leave policy for secondary caregivers?",
    "Do sick days roll over to the next year?",
]


def tok(text: str) -> int:
    return len(enc.encode(text))


def chunk_fixed(text: str, size: int, overlap: int) -> list[str]:
    tokens = enc.encode(text)
    chunks, start = [], 0
    while start < len(tokens):
        chunks.append(enc.decode(tokens[start:start + size]))
        start += size - overlap
    return chunks


def chunk_sentence(text: str, max_tok: int) -> list[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks, cur, count = [], [], 0
    for s in sentences:
        st = tok(s)
        if count + st > max_tok and cur:
            chunks.append(" ".join(cur))
            cur, count = [], 0
        cur.append(s)
        count += st
    if cur:
        chunks.append(" ".join(cur))
    return chunks


def evaluate_chunking(strategy_name: str, chunks: list[str], queries: list[str]) -> dict:
    """
    Builds a tiny ChromaDB collection from the chunks and runs each query,
    checking if the relevant chunk is retrieved in top-1.
    """
    chroma  = chromadb.EphemeralClient()   # In-memory — no files written
    embed   = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    col = chroma.create_collection(name=strategy_name, embedding_function=embed)
    col.add(
        ids=[f"c{i}" for i in range(len(chunks))],
        documents=chunks,
    )

    hits = 0
    for query in queries:
        results = col.query(query_texts=[query], n_results=1)
        top_chunk = results["documents"][0][0]
        # Simple relevance check: does the top chunk contain key query terms?
        query_words = set(query.lower().split())
        chunk_words = set(top_chunk.lower().split())
        overlap = len(query_words & chunk_words)
        if overlap >= 2:
            hits += 1

    return {
        "strategy":  strategy_name,
        "n_chunks":  len(chunks),
        "avg_tokens": sum(tok(c) for c in chunks) // len(chunks),
        "retrieval_hits": hits,
        "retrieval_pct":  round(hits / len(queries) * 100),
    }


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 4 — Chunking Strategy Comparison[/bold]\n")

    strategies = [
        ("Fixed-50 (no overlap)",    chunk_fixed(SAMPLE_DOCUMENT, 50, 0)),
        ("Fixed-100 (10 overlap)",   chunk_fixed(SAMPLE_DOCUMENT, 100, 10)),
        ("Fixed-200 (20 overlap)",   chunk_fixed(SAMPLE_DOCUMENT, 200, 20)),
        ("Sentence-aware (max 100)", chunk_sentence(SAMPLE_DOCUMENT, 100)),
        ("Sentence-aware (max 200)", chunk_sentence(SAMPLE_DOCUMENT, 200)),
    ]

    table = Table(title="Chunking Strategy Comparison")
    table.add_column("Strategy",        style="cyan", width=28)
    table.add_column("# Chunks",        justify="right")
    table.add_column("Avg tokens",      justify="right")
    table.add_column("Retrieval hits",  justify="right")
    table.add_column("Hit rate",        justify="right")

    best = None
    for name, chunks in strategies:
        result = evaluate_chunking(name.replace(" ", "_"), chunks, QUERIES)
        is_best = best is None or result["retrieval_pct"] > best["retrieval_pct"]
        if is_best:
            best = result
        style = "bold green" if is_best else ""
        table.add_row(
            f"[{style}]{name}[/{style}]" if style else name,
            str(result["n_chunks"]),
            str(result["avg_tokens"]),
            str(result["retrieval_hits"]),
            f"{result['retrieval_pct']}%",
        )

    console.print(table)
    console.print(
        f"\n[bold]Best strategy:[/bold] {best['strategy']} — "
        f"{best['retrieval_hits']}/{len(QUERIES)} queries retrieved correctly.\n"
        "\n[bold]Lesson:[/bold] Sentence-aware chunking at 150-200 tokens generally outperforms "
        "fixed-size chunking because it avoids cutting sentences mid-thought, "
        "producing more coherent embeddings.\n"
    )
