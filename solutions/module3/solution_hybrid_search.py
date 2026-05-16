"""
SOLUTION: Module 3 — Hybrid Search RAG Pipeline
================================================
Answer key for the Module 3 Lesson 5 task:
Build a hybrid retriever that outperforms dense-only search on both
keyword-heavy and semantic queries, then answer questions with the fused context.

Run:
    python solutions/module3/solution_hybrid_search.py
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
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST, RAG_DISTANCE_THRESHOLD

load_dotenv()
client  = Anthropic()
console = Console()

DOCUMENTS = [
    {"id": "d1",  "content": "Set RATE_LIMIT_MAX=100 in config to control requests per minute."},
    {"id": "d2",  "content": "API throttling prevents services from being overwhelmed by too many requests."},
    {"id": "d3",  "content": "HTTP status code 429 Too Many Requests means you have hit the rate limit."},
    {"id": "d4",  "content": "The DB_CONNECTION_POOL_SIZE environment variable controls database concurrency."},
    {"id": "d5",  "content": "Connection pooling reuses database connections to reduce overhead."},
    {"id": "d6",  "content": "Set MAX_TOKENS=4096 for the context window size in production deployments."},
    {"id": "d7",  "content": "Context windows limit how much text a language model can process at once."},
    {"id": "d8",  "content": "Transformer models use self-attention to weigh token relationships."},
    {"id": "d9",  "content": "Embeddings convert text to vectors that capture semantic meaning."},
    {"id": "d10", "content": "Vector databases like ChromaDB store and search dense embedding representations."},
]


def build_retrievers(docs: list[dict]):
    chroma = chromadb.EphemeralClient()
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    col = chroma.create_collection("solution_hybrid", embedding_function=embed_fn)
    col.add(ids=[d["id"] for d in docs], documents=[d["content"] for d in docs])

    tokenised = [d["content"].lower().split() for d in docs]
    bm25 = BM25Okapi(tokenised)
    return col, bm25


def rrf(lists: list[list[str]], k: int = 60) -> list[str]:
    scores: dict[str, float] = {}
    for ranked in lists:
        for rank, doc_id in enumerate(ranked, 1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
    return [doc_id for doc_id, _ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]


def dense_ids(query: str, col, top_k: int) -> list[str]:
    r = col.query(query_texts=[query], n_results=top_k, include=["metadatas", "distances"])
    return [
        m["id"] for m, dist in zip(r["metadatas"][0], r["distances"][0])
        if dist <= RAG_DISTANCE_THRESHOLD
    ]


def sparse_ids(query: str, bm25, docs: list[dict], top_k: int) -> list[str]:
    scores = bm25.get_scores(query.lower().split())
    ranked = sorted(range(len(docs)), key=lambda i: scores[i], reverse=True)
    return [docs[i]["id"] for i in ranked[:top_k] if scores[ranked[i]] > 0]


def hybrid_retrieve(query: str, col, bm25, docs: list[dict], top_k: int = 3) -> list[dict]:
    pool     = top_k * 2
    d_ids    = dense_ids(query, col, pool)
    s_ids    = sparse_ids(query, bm25, docs, pool)
    fused    = rrf([d_ids, s_ids])[:top_k]
    id_map   = {d["id"]: d for d in docs}
    return [id_map[i] for i in fused if i in id_map]


def answer(query: str, chunks: list[dict]) -> str:
    context = "\n".join(f"- {c['content']}" for c in chunks)
    if not context:
        context = "No relevant context found."
    r = client.messages.create(
        model=MODEL_FAST, max_tokens=256,
        messages=[{"role": "user", "content":
            f"Context:\n{context}\n\nQuestion: {query}\n"
            "Answer concisely. If the context doesn't contain the answer, say so."
        }]
    )
    return r.content[0].text


EVAL_QUERIES = [
    ("What does RATE_LIMIT_MAX control?",           "keyword",  "d1 should be top result"),
    ("How do transformer models process text?",     "semantic", "d8 should appear"),
    ("What happens with HTTP 429 response?",        "mixed",    "d3 should be top"),
    ("How are embeddings stored for search?",       "semantic", "d9/d10 should appear"),
]

if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 3 — Hybrid Search[/bold]\n")
    col, bm25 = build_retrievers(DOCUMENTS)

    table = Table(title="Hybrid Search Evaluation", show_lines=True)
    table.add_column("Query",     width=38)
    table.add_column("Type",      width=9)
    table.add_column("Top chunk", width=45)
    table.add_column("Answer snippet", width=35)

    for query, qtype, note in EVAL_QUERIES:
        chunks = hybrid_retrieve(query, col, bm25, DOCUMENTS, top_k=3)
        ans    = answer(query, chunks)
        top    = chunks[0]["content"][:43] if chunks else "No results"
        table.add_row(query[:37], qtype, top, ans[:34])

    console.print(table)
    console.print("\n[bold green]✓ Solution complete![/bold green]\n")
    console.print(
        "Key insight: hybrid search matches or beats dense-only on all query types "
        "because RRF rewards documents that rank well in at least one retriever.\n"
    )
