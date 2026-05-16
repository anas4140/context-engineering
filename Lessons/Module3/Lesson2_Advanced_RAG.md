# **Module 3, Lesson 2: Advanced RAG — Metadata Filtering & Hybrid Search**

Building on the basic pipeline, this lesson adds three production-grade retrieval techniques.

---

## Learning Objectives

- **Build** metadata-filtered retrieval to restrict search to specific sources
- **Implement** multi-query RAG to improve recall on ambiguous queries
- **Apply** hybrid search combining vector similarity and keyword matching

---

## 1. Metadata Filtering

ChromaDB lets you attach metadata (source filename, page, date, department) to each document chunk and filter on it at query time.

**Use cases:**
- "Only search the finance_policy.pdf, not the employee handbook"
- "Only retrieve documents published after 2023"
- "Only return chunks from the Engineering department's wiki"

```python
# Filter to a specific source file
results = collection.query(
    query_texts=[query],
    n_results=3,
    where={"source": {"$eq": "finance_policy.pdf"}}
)
```

This runs the metadata filter *before* the vector search — only matching documents are candidates.

## 2. Multi-Query RAG

A single query phrasing may miss relevant chunks that use different vocabulary. Generate 2–3 rephrased versions of the question, retrieve for each, then deduplicate.

**Example:**
- Original: "vacation days rollover"
- Variant 1: "Can unused PTO carry over to the next year?"
- Variant 2: "What happens to annual leave I don't use?"

Each phrasing may surface different relevant chunks. Deduplication by content ensures no chunk appears twice in the final context.

## 3. Hybrid Search

Vector search finds semantically similar chunks. Keyword search finds exact matches. Hybrid combines both — chunks matching both signals rank highest.

**When pure vector search fails:** Highly specific terms (product model numbers, person names, legal clause references) may not embed well. A keyword match catches them.

---

## Hands-On Task

Run:

```bash
python code/module3/lesson2_advanced_rag.py
```

Then:

1. Add a `date` field to each document's metadata and filter to documents newer than a specific date
2. Test multi-query on a very broad question ("tell me about company policies"). How many unique chunks are returned vs a single query?
3. Identify a query where hybrid search outperforms pure vector search. What type of query is it?

---

*Next: [Lesson 3 — RAG Evaluation](Lesson3_RAG_Evaluation.md)*
