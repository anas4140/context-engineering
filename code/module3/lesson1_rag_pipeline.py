"""
Module 3: Full RAG Pipeline
============================
This is the most important file in Module 3. It implements a complete,
working Retrieval-Augmented Generation (RAG) pipeline from scratch using:
  - ChromaDB  — local vector store (persists to disk)
  - sentence-transformers — converts text to vectors (embeddings)
  - Anthropic Claude — generates the final answer

Architecture:
  Documents → Chunk → Embed → Store in ChromaDB
  User Query → Embed → Search ChromaDB → Retrieve top-k chunks
  Chunks + Query → Claude → Cited Answer

Run:
    python code/module3/lesson1_rag_pipeline.py
"""

import os
from pathlib import Path
from anthropic import Anthropic
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

load_dotenv()
client    = Anthropic()
console   = Console()

# ─────────────────────────────────────────────
#  STEP 0 — Sample documents
#  In a real system these would come from your
#  company wiki, PDF files, or a database.
#  We hard-code them here for simplicity.
# ─────────────────────────────────────────────
SAMPLE_DOCUMENTS = [
    {
        "id":      "hr_pto_001",
        "source":  "employee_handbook.pdf",
        "page":    12,
        "content": (
            "Time Off Policy: Full-time employees receive 20 days of Paid Time "
            "Off (PTO) per year. PTO accrues at a rate of 1.67 days per month. "
            "Unused PTO can be rolled over, up to a maximum of 10 days. New "
            "employees start with a balance of 0 days and begin accruing PTO "
            "on their first day of employment."
        ),
    },
    {
        "id":      "hr_benefits_001",
        "source":  "employee_handbook.pdf",
        "page":    18,
        "content": (
            "Health Benefits: All full-time employees are eligible for health "
            "insurance from day one. The company covers 80% of the premium for "
            "the employee and 50% for dependants. Dental and vision plans are "
            "available at an additional cost. Open enrolment runs each November."
        ),
    },
    {
        "id":      "hr_remote_001",
        "source":  "employee_handbook.pdf",
        "page":    24,
        "content": (
            "Remote Work Policy: Employees may work remotely up to 3 days per "
            "week with manager approval. A fully remote arrangement requires VP "
            "sign-off and a written agreement. Remote employees must be available "
            "during core hours of 10 AM – 3 PM in their local time zone."
        ),
    },
    {
        "id":      "hr_performance_001",
        "source":  "employee_handbook.pdf",
        "page":    31,
        "content": (
            "Performance Reviews: Reviews are conducted twice a year, in June "
            "and December. Each review consists of a self-assessment, a manager "
            "assessment, and a calibration meeting. Salary increases are linked "
            "to performance ratings and are effective from the first of the "
            "following month after the review."
        ),
    },
    {
        "id":      "hr_expense_001",
        "source":  "finance_policy.pdf",
        "page":    5,
        "content": (
            "Expense Reimbursement: Business expenses up to $50 can be submitted "
            "without a receipt. Expenses between $50 and $500 require a receipt "
            "and manager approval. Expenses over $500 require a receipt, manager "
            "approval, and Finance sign-off. Submit all expenses within 30 days "
            "of the purchase via the Expensify portal."
        ),
    },
]


# ─────────────────────────────────────────────
#  STEP 1 — Build the vector store
#  Each document is converted to a vector
#  (embedding) and stored in ChromaDB.
# ─────────────────────────────────────────────
def build_knowledge_base(documents: list[dict], persist_dir: str = "./chroma_db") -> chromadb.Collection:
    """
    Takes a list of document dicts and stores them in a local ChromaDB collection.
    On subsequent runs it loads the existing collection instead of rebuilding.

    Args:
        documents: list of dicts with keys: id, source, page, content
        persist_dir: where ChromaDB saves its files on disk

    Returns:
        A ChromaDB Collection object ready for querying
    """
    console.print(f"  Initialising ChromaDB at [cyan]{persist_dir}[/cyan]")

    # PersistentClient saves the vector store to disk so you don't
    # have to re-embed every time you restart the script.
    chroma_client = chromadb.PersistentClient(path=persist_dir)

    # sentence-transformers/all-MiniLM-L6-v2 is a small, fast model
    # that produces good embeddings for English text.
    # It downloads automatically on first run (~90 MB).
    embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # get_or_create means we reuse an existing collection if it exists
    collection = chroma_client.get_or_create_collection(
        name="hr_documents",
        embedding_function=embed_fn,
        metadata={"description": "HR and Finance policy documents"}
    )

    # Only add documents if the collection is empty
    # (avoids duplicate errors on re-runs)
    if collection.count() == 0:
        console.print(f"  Embedding {len(documents)} documents...")

        collection.add(
            ids       = [doc["id"]      for doc in documents],
            documents = [doc["content"] for doc in documents],
            # Metadata lets us filter by source or display citations later
            metadatas = [{"source": doc["source"], "page": doc["page"]}
                         for doc in documents],
        )
        console.print(f"  [green]✓ {collection.count()} documents stored[/green]")
    else:
        console.print(f"  [green]✓ Loaded existing collection ({collection.count()} docs)[/green]")

    return collection


# ─────────────────────────────────────────────
#  STEP 2 — Retrieve relevant chunks
#  Given a user question, find the most
#  semantically similar documents in ChromaDB.
# ─────────────────────────────────────────────
def retrieve(query: str, collection: chromadb.Collection, top_k: int = 2) -> list[dict]:
    """
    Searches ChromaDB for the top_k most relevant chunks for a given query.
    ChromaDB automatically embeds the query using the same model.

    Args:
        query:      the user's question
        collection: the ChromaDB collection to search
        top_k:      how many results to return (usually 2–5)

    Returns:
        list of dicts with keys: content, source, page, distance
    """
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        include=["documents", "metadatas", "distances"]
    )

    # Unpack the nested results structure
    chunks = []
    for doc, meta, dist in zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    ):
        chunks.append({
            "content":  doc,
            "source":   meta["source"],
            "page":     meta["page"],
            # Lower distance = more similar (ChromaDB uses L2 distance)
            "distance": round(dist, 4),
        })
    return chunks


# ─────────────────────────────────────────────
#  STEP 3 — Generate the answer
#  Pass the retrieved chunks to Claude as
#  context and ask it to answer the question.
# ─────────────────────────────────────────────
def generate_answer(query: str, chunks: list[dict]) -> str:
    """
    Builds a prompt containing the retrieved chunks and asks Claude to
    synthesise an answer with citations.

    Args:
        query:  the user's question
        chunks: list of retrieved document chunks from retrieve()

    Returns:
        Claude's answer as a string
    """

    # Format the retrieved chunks for the prompt
    # We include source + page so the model can cite them
    context_block = ""
    for i, chunk in enumerate(chunks, start=1):
        context_block += (
            f"[Source {i}: {chunk['source']}, page {chunk['page']}]\n"
            f"{chunk['content']}\n\n"
        )

    system_prompt = (
        "You are a helpful HR assistant. "
        "Answer the employee's question using ONLY the information in the "
        "<context> tags below. "
        "Always cite your source (e.g. 'According to employee_handbook.pdf, page 12...'). "
        "If the answer is not in the context, say exactly: "
        "'I don't have that information in the provided documents.'"
    )

    user_message = f"""<context>
{context_block}</context>

Employee question: {query}"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


# ─────────────────────────────────────────────
#  STEP 4 — Full pipeline wrapper
#  Ties retrieve() + generate() together.
# ─────────────────────────────────────────────
def ask(query: str, collection: chromadb.Collection, top_k: int = 2) -> dict:
    """
    The complete RAG pipeline in one function call.

    Returns a dict with:
        answer   — Claude's response
        sources  — list of retrieved chunks used
    """
    # Retrieve the most relevant document chunks
    chunks = retrieve(query, collection, top_k=top_k)

    # Generate an answer grounded in those chunks
    answer = generate_answer(query, chunks)

    return {"answer": answer, "sources": chunks}


if __name__ == "__main__":
    console.print("\n[bold]Module 3: RAG Pipeline Demo[/bold]\n")

    # ── Build / load the knowledge base ──────
    console.print(Rule("Step 1: Build knowledge base"))
    collection = build_knowledge_base(SAMPLE_DOCUMENTS)

    # ── Run some test queries ─────────────────
    test_queries = [
        "How much vacation time do I get, and can I roll it over?",
        "Can I work from home every day?",
        "How do I submit an expense for a $200 business lunch?",
        "What is the capital of France?",   # ← not in documents — tests fallback
    ]

    console.print(Rule("Step 2: Query the RAG system"))
    for query in test_queries:
        console.print(f"\n[bold yellow]Q: {query}[/bold yellow]")
        result = ask(query, collection)

        console.print(Panel(result["answer"], title="Answer"))

        # Print which sources were used
        for chunk in result["sources"]:
            console.print(
                f"  [dim]↳ Retrieved: {chunk['source']} p.{chunk['page']} "
                f"(distance: {chunk['distance']})[/dim]"
            )

    console.print("\n[bold green]✓ Module 3 RAG pipeline complete![/bold green]")
    console.print("Next: [italic]python code/module4/lesson2_compression.py[/italic]\n")
