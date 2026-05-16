"""
Module 3, Lesson 3: Hybrid Search
===================================
Demonstrates combining dense vector search (ChromaDB) with sparse BM25
retrieval, fused via Reciprocal Rank Fusion (RRF) for higher recall.

Run:
    python code/module3/lesson3_hybrid_search.py
"""

import os
import sys
from rank_bm25 import BM25Okapi
import chromadb
from chromadb.utils import embedding_functions
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

# ─────────────────────────────────────────────
#  Sample knowledge base with keyword-heavy and
#  semantic-heavy documents to show the contrast
# ─────────────────────────────────────────────
DOCUMENTS = [
    {"id": "doc-1", "content": "The MAX_UPLOAD_SIZE constant controls the maximum file upload limit in bytes."},
    {"id": "doc-2", "content": "Users can upload files to cloud storage for sharing and collaboration."},
    {"id": "doc-3", "content": "HTTP 429 Too Many Requests indicates the client has exceeded the rate limit."},
    {"id": "doc-4", "content": "Rate limiting protects APIs from being overwhelmed by too many requests."},
    {"id": "doc-5", "content": "The configuration file stores API keys, database credentials, and feature flags."},
    {"id": "doc-6", "content": "Environment variables like API_KEY and DB_PASSWORD should never be committed to git."},
    {"id": "doc-7", "content": "Neural networks learn by adjusting weights to minimise a loss function."},
    {"id": "doc-8", "content": "Backpropagation computes the gradient of the loss with respect to each weight."},
]


# ─────────────────────────────────────────────
#  Build retrievers
# ─────────────────────────────────────────────
def build_dense(documents: list[dict]) -> chromadb.Collection:
    chroma = chromadb.EphemeralClient()
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    col = chroma.create_collection("hybrid_demo", embedding_function=embed_fn)
    col.add(
        ids       = [d["id"]      for d in documents],
        documents = [d["content"] for d in documents],
    )
    return col


def build_sparse(documents: list[dict]) -> BM25Okapi:
    tokenised = [d["content"].lower().split() for d in documents]
    return BM25Okapi(tokenised)


# ─────────────────────────────────────────────
#  Reciprocal Rank Fusion
# ─────────────────────────────────────────────
def rrf(ranked_lists: list[list[str]], k: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, 1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return [doc_id for doc_id, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]


# ─────────────────────────────────────────────
#  Retrievers
# ─────────────────────────────────────────────
def dense_retrieve(query: str, col: chromadb.Collection, top_k: int) -> list[str]:
    results = col.query(query_texts=[query], n_results=top_k, include=["metadatas"])
    return [m["id"] for m in results["metadatas"][0]]


def sparse_retrieve(query: str, bm25: BM25Okapi, documents: list[dict], top_k: int) -> list[str]:
    scores = bm25.get_scores(query.lower().split())
    ranked = sorted(range(len(documents)), key=lambda i: scores[i], reverse=True)
    return [documents[i]["id"] for i in ranked[:top_k]]


def hybrid_retrieve(
    query: str,
    col: chromadb.Collection,
    bm25: BM25Okapi,
    documents: list[dict],
    top_k: int = 3,
) -> list[dict]:
    pool    = top_k * 2
    dense   = dense_retrieve(query, col, pool)
    sparse  = sparse_retrieve(query, bm25, documents, pool)
    fused   = rrf([dense, sparse])[:top_k]
    id_map  = {d["id"]: d for d in documents}
    return [id_map[doc_id] for doc_id in fused if doc_id in id_map]


def answer_with_context(query: str, chunks: list[dict]) -> str:
    context = "\n".join(f"- {c['content']}" for c in chunks)
    r = client.messages.create(
        model=MODEL_FAST, max_tokens=256,
        messages=[{"role": "user", "content":
            f"Context:\n{context}\n\nQuestion: {query}\nAnswer concisely."
        }]
    )
    return r.content[0].text


if __name__ == "__main__":
    console.print("\n[bold]Module 3, Lesson 3 — Hybrid Search[/bold]\n")

    col  = build_dense(DOCUMENTS)
    bm25 = build_sparse(DOCUMENTS)

    test_queries = [
        ("MAX_UPLOAD_SIZE limit in bytes",   "keyword-heavy — BM25 should win"),
        ("how do neural networks learn",     "semantic — dense should win"),
        ("API rate limit HTTP error code",   "mixed — both contribute"),
        ("secret credentials in git",        "semantic + keyword mix"),
    ]

    for query, note in test_queries:
        console.print(Rule(f"[dim]{note}[/dim]"))
        console.print(f"[yellow]Query:[/yellow] {query}\n")

        d_results = dense_retrieve(query, col, top_k=3)
        s_results = sparse_retrieve(query, bm25, DOCUMENTS, top_k=3)
        h_results = hybrid_retrieve(query, col, bm25, DOCUMENTS, top_k=3)

        table = Table(show_lines=True)
        table.add_column("Rank")
        table.add_column("Dense",  width=40)
        table.add_column("Sparse", width=40)
        table.add_column("Hybrid (RRF)", width=40)

        id_map = {d["id"]: d["content"] for d in DOCUMENTS}
        for i in range(3):
            table.add_row(
                str(i + 1),
                id_map.get(d_results[i] if i < len(d_results) else "", "—")[:38],
                id_map.get(s_results[i] if i < len(s_results) else "", "—")[:38],
                id_map.get(h_results[i]["id"] if i < len(h_results) else "", "—")[:38],
            )
        console.print(table)

        answer = answer_with_context(query, h_results)
        console.print(Panel(answer, title="[green]Answer (hybrid context)[/green]"))
        console.print()

    console.print("[bold green]✓ Lesson 3 complete![/bold green]")
    console.print("Next: [italic]python code/module4/lesson1_anatomy.py[/italic]\n")
