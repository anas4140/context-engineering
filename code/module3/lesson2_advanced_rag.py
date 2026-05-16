"""
Module 3, Lesson 2: Advanced RAG — Metadata Filtering & Hybrid Search
=======================================================================
Extends the basic RAG pipeline with:
  1. Metadata filtering — restrict search to a specific source file or page range
  2. Hybrid search     — combine vector similarity + keyword match
  3. Multi-query RAG   — generate multiple query variants to improve recall

Run:
    python code/module3/lesson2_advanced_rag.py
"""

import os
import re
from anthropic import Anthropic
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

load_dotenv()
client  = Anthropic()
console = Console()
MODEL   = "claude-haiku-4-5-20251001"


# Reuse the sample docs from Lesson 1 — also add source variety for filtering demo
DOCUMENTS = [
    {"id": "hr_pto",        "source": "employee_handbook.pdf", "page": 12, "content": "Full-time employees receive 20 days of Paid Time Off (PTO) per year. PTO accrues at 1.67 days per month. Up to 10 unused days can be rolled over annually."},
    {"id": "hr_health",     "source": "employee_handbook.pdf", "page": 18, "content": "Health insurance is available from day one. The company covers 80% of the premium. Dental and vision plans are also available at additional cost."},
    {"id": "hr_remote",     "source": "employee_handbook.pdf", "page": 24, "content": "Employees may work remotely up to 3 days per week with manager approval. Core hours are 10 AM – 3 PM local time."},
    {"id": "fin_expense",   "source": "finance_policy.pdf",    "page": 5,  "content": "Expenses up to $50 need no receipt. $50-$500 require a receipt and manager approval. Over $500 requires Finance sign-off. Submit within 30 days via Expensify."},
    {"id": "fin_budget",    "source": "finance_policy.pdf",    "page": 9,  "content": "Each department has an annual budget allocated in January. Budget transfers between departments require CFO approval. Unspent budgets do not roll over."},
    {"id": "it_security",   "source": "it_security_policy.pdf","page": 3,  "content": "All company laptops must use full-disk encryption. Passwords must be at least 16 characters and changed every 90 days. VPN is required when accessing company systems remotely."},
]


def build_collection(docs: list[dict], name: str = "advanced_rag") -> chromadb.Collection:
    chroma = chromadb.PersistentClient(path="./chroma_advanced")
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    col = chroma.get_or_create_collection(name=name, embedding_function=embed_fn)
    if col.count() == 0:
        col.add(
            ids       = [d["id"]      for d in docs],
            documents = [d["content"] for d in docs],
            metadatas = [{"source": d["source"], "page": d["page"]} for d in docs],
        )
    return col


# ─────────────────────────────────────────────
#  TECHNIQUE 1: Metadata filtering
#  Restrict the vector search to documents from
#  a specific source file, department, or date.
# ─────────────────────────────────────────────
def retrieve_with_filter(
    query: str,
    collection: chromadb.Collection,
    source_filter: str | None = None,
    top_k: int = 2
) -> list[dict]:
    """
    Retrieves chunks optionally filtered by source filename.
    ChromaDB's `where` clause filters BEFORE the vector search.

    Args:
        source_filter: if set, only return chunks from this source file
    """
    kwargs = {
        "query_texts": [query],
        "n_results":   top_k,
        "include":     ["documents", "metadatas", "distances"],
    }
    if source_filter:
        # ChromaDB filter syntax: {"metadata_key": {"$eq": "value"}}
        kwargs["where"] = {"source": {"$eq": source_filter}}

    results = collection.query(**kwargs)
    return [
        {"content": doc, "source": meta["source"], "page": meta["page"]}
        for doc, meta in zip(results["documents"][0], results["metadatas"][0])
    ]


# ─────────────────────────────────────────────
#  TECHNIQUE 2: Multi-query RAG
#  Generate multiple phrasings of the user's
#  question, retrieve for each, then deduplicate.
#  Improves recall for ambiguous or broad queries.
# ─────────────────────────────────────────────
def generate_query_variants(original_query: str, n: int = 3) -> list[str]:
    """
    Asks Claude to rephrase the user's query in `n` different ways.
    Different phrasings match different chunks in the vector store.
    """
    prompt = (
        f"Generate {n} different phrasings of this question that preserve its meaning "
        f"but use different vocabulary. Return ONLY the questions, one per line, "
        f"no numbering or extra text.\n\nOriginal: {original_query}"
    )
    response = client.messages.create(
        model=MODEL, max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    variants = [line.strip() for line in response.content[0].text.strip().split("\n") if line.strip()]
    # Always include the original
    return [original_query] + variants[:n]


def multi_query_retrieve(
    query: str,
    collection: chromadb.Collection,
    n_variants: int = 2,
    top_k_per_query: int = 2
) -> list[dict]:
    """
    Generates multiple query variants, retrieves for each, deduplicates by content.
    Returns a merged list of unique chunks.
    """
    variants = generate_query_variants(query, n=n_variants)
    console.print(f"  [dim]Query variants: {variants}[/dim]")

    seen_contents = set()
    all_chunks    = []

    for variant in variants:
        chunks = retrieve_with_filter(variant, collection, top_k=top_k_per_query)
        for chunk in chunks:
            # Deduplicate by content
            if chunk["content"] not in seen_contents:
                seen_contents.add(chunk["content"])
                all_chunks.append(chunk)

    return all_chunks


# ─────────────────────────────────────────────
#  TECHNIQUE 3: Keyword-boosted hybrid search
#  ChromaDB is vector-only, so we simulate
#  hybrid search by running a keyword filter
#  alongside the vector search and merging.
# ─────────────────────────────────────────────
def hybrid_retrieve(
    query: str,
    collection: chromadb.Collection,
    top_k: int = 3
) -> list[dict]:
    """
    Combines vector search results with a simple keyword match on the documents.
    Chunks matching both are ranked higher.
    """
    # Vector search
    vector_results = retrieve_with_filter(query, collection, top_k=top_k)

    # Keyword match — find documents containing query words
    query_words = set(re.findall(r'\b\w{4,}\b', query.lower()))  # 4+ char words
    all_docs    = collection.get(include=["documents", "metadatas"])

    keyword_matches = []
    for doc, meta in zip(all_docs["documents"], all_docs["metadatas"]):
        doc_words = set(re.findall(r'\b\w{4,}\b', doc.lower()))
        overlap   = len(query_words & doc_words)
        if overlap > 0:
            keyword_matches.append({
                "content": doc, "source": meta["source"],
                "page": meta["page"], "keyword_score": overlap
            })

    # Merge: prefer chunks that appear in BOTH results
    vector_contents = {c["content"] for c in vector_results}
    merged = []

    # Chunks in both → highest priority
    for km in keyword_matches:
        if km["content"] in vector_contents:
            km["hybrid"] = True
            merged.append(km)

    # Then vector-only results
    for vc in vector_results:
        if not any(m["content"] == vc["content"] for m in merged):
            vc["hybrid"] = False
            merged.append(vc)

    return merged[:top_k]


if __name__ == "__main__":
    console.print("\n[bold]Module 3, Lesson 2: Advanced RAG Techniques[/bold]\n")

    col = build_collection(DOCUMENTS)

    # ── Metadata filtering ────────────────────
    console.print(Rule("Technique 1: Metadata filtering"))

    q = "What are the rules about working from home?"

    unfiltered = retrieve_with_filter(q, col, source_filter=None)
    filtered   = retrieve_with_filter(q, col, source_filter="employee_handbook.pdf")

    console.print(f"\nQuery: [yellow]{q}[/yellow]")
    console.print("\nWithout filter:")
    for c in unfiltered:
        console.print(f"  [{c['source']}] {c['content'][:70]}...")
    console.print("\nFiltered to employee_handbook.pdf only:")
    for c in filtered:
        console.print(f"  [{c['source']}] {c['content'][:70]}...")

    # ── Multi-query RAG ───────────────────────
    console.print(Rule("\nTechnique 2: Multi-query RAG"))

    q2 = "vacation days rollover"
    chunks = multi_query_retrieve(q2, col, n_variants=2)
    console.print(f"\nQuery: [yellow]{q2}[/yellow]  →  {len(chunks)} unique chunks retrieved")
    for c in chunks:
        console.print(f"  [{c['source']} p.{c['page']}] {c['content'][:80]}...")

    # ── Hybrid search ─────────────────────────
    console.print(Rule("\nTechnique 3: Hybrid search"))

    q3 = "expense reimbursement receipt required"
    hybrid_chunks = hybrid_retrieve(q3, col)
    console.print(f"\nQuery: [yellow]{q3}[/yellow]")
    for c in hybrid_chunks:
        tag = "[green]VECTOR+KEYWORD[/green]" if c.get("hybrid") else "[dim]vector only[/dim]"
        console.print(f"  {tag} [{c['source']}] {c['content'][:80]}...")

    console.print("\n[bold green]✓ Module 3 Lesson 2 complete![/bold green]\n")
