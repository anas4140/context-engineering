# **Module 3, Lesson 5: Hybrid Search**

Dense vector search excels at semantic similarity but misses exact keyword matches. Sparse BM25 excels at keywords but misses paraphrases. Hybrid search combines both signals for higher recall and precision.

---

## Learning Objectives

- **Explain** why dense-only search fails on exact keyword queries
- **Implement** BM25 sparse retrieval with `rank-bm25`
- **Fuse** dense and sparse scores using Reciprocal Rank Fusion (RRF)

---

## 1. The Problem with Dense-Only Search

Dense embeddings encode semantic meaning. The sentence *"the maximum upload file size"* and *"MAX_FILE_SIZE"* have very different embeddings despite referring to the same concept.

Query: `"MAX_FILE_SIZE limit"`
- Dense search: returns "file storage policies" (semantically close) ✓
- Dense search: misses the document containing the literal string "MAX_FILE_SIZE" ✗
- BM25: finds "MAX_FILE_SIZE" documents instantly ✓

---

## 2. BM25 Sparse Retrieval

BM25 scores documents by term frequency and inverse document frequency:

```python
from rank_bm25 import BM25Okapi

corpus = [
    "The maximum file size is MAX_FILE_SIZE bytes",
    "Upload limits vary by account tier",
    "Storage quotas reset monthly",
]

tokenised = [doc.lower().split() for doc in corpus]
bm25      = BM25Okapi(tokenised)

query   = "MAX_FILE_SIZE limit"
scores  = bm25.get_scores(query.lower().split())
# → array([2.1, 0.3, 0.0])  ← first doc wins on keywords
```

---

## 3. Reciprocal Rank Fusion (RRF)

RRF combines ranked lists from multiple retrievers without needing to normalise scores:

```
RRF_score(doc) = Σ  1 / (k + rank_i(doc))
```

Where `k=60` is a smoothing constant and `rank_i` is the document's position in retriever `i`.

```python
def reciprocal_rank_fusion(
    dense_ids: list[str],
    sparse_ids: list[str],
    k: int = 60,
) -> list[tuple[str, float]]:
    scores: dict[str, float] = {}
    for rank, doc_id in enumerate(dense_ids, 1):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    for rank, doc_id in enumerate(sparse_ids, 1):
        scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
```

---

## 4. Full Hybrid Retrieval Pipeline

```python
def hybrid_retrieve(
    query: str,
    collection: chromadb.Collection,
    bm25: BM25Okapi,
    documents: list[dict],
    top_k: int = 3,
) -> list[dict]:
    # ── Dense retrieval (ChromaDB) ────────────────────────────────────
    dense_results = collection.query(
        query_texts=[query], n_results=top_k * 2,
        include=["documents", "metadatas", "distances"]
    )
    dense_ids = [m["id"] for m in dense_results["metadatas"][0]]

    # ── Sparse retrieval (BM25) ───────────────────────────────────────
    bm25_scores = bm25.get_scores(query.lower().split())
    sparse_ranking = sorted(
        range(len(documents)), key=lambda i: bm25_scores[i], reverse=True
    )
    sparse_ids = [documents[i]["id"] for i in sparse_ranking[:top_k * 2]]

    # ── Fuse with RRF ─────────────────────────────────────────────────
    fused = reciprocal_rank_fusion(dense_ids, sparse_ids)
    top_ids = [doc_id for doc_id, _ in fused[:top_k]]

    id_to_doc = {d["id"]: d for d in documents}
    return [id_to_doc[doc_id] for doc_id in top_ids if doc_id in id_to_doc]
```

---

## 5. When Each Mode Wins

| Query type | Dense wins | BM25 wins |
|------------|-----------|-----------|
| "explain photosynthesis" | ✓ | — |
| "MAX_FILE_SIZE constant" | — | ✓ |
| "user ID 4829 error" | — | ✓ |
| "how do I upload a file" | ✓ | — |
| "HTTP 429 rate limit" | ✓ | ✓ both |

Hybrid always matches or beats either alone.

---

## Key Takeaways

- Dense search misses exact keyword/identifier matches; BM25 misses paraphrases
- RRF fuses ranked lists without score normalisation — simple and effective
- Hybrid search is the production default for most RAG systems
- Retrieve `top_k × 2` from each retriever before fusing, then trim to `top_k`

---

*Up next: Module 4 — Token Budget & Compression*

---

## Hands-On Task

Run the hybrid search demo:

```bash
python code/module3/lesson5_hybrid_search.py
```

Then try:

1. **Beat dense-only**: Add a document containing a product code like `SKU-XR7-ALPHA` to the `DOCS` list. Query for `SKU-XR7-ALPHA` and compare dense vs hybrid results. Which finds it?
2. **Tune the k parameter**: In the `rrf()` function, change `k=60` to `k=5` and then `k=200`. How does it affect the ranking when two retrievers disagree?
3. **Mixed query**: Write a query that has both a semantic component ("how does it work") and a keyword component (a specific term). Does hybrid search return a better top result than either alone?

---

*Next: [Module 4 — Optimising the Context Window](../Module4/Lesson1_Context_Window_Anatomy.md)*
