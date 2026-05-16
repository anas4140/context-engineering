# **Module 4, Lesson 2: Compression Techniques**

When the context window fills up, compress rather than discard. This lesson covers three techniques that reduce token count while preserving information density.

---

## Learning Objectives

- **Build** fixed-size and sentence-aware chunking
- **Implement** contextual compression using the LLM
- **Apply** re-ranking to prioritise the most relevant chunks

---

## 1. Chunking Strategies

| Chunk size | Best for | Trade-off |
|---|---|---|
| Small (50-100 tokens) | Precise fact retrieval | Loses surrounding context |
| Medium (200-400 tokens) | General Q&A | Good balance |
| Large (500-1000 tokens) | Summarisation | Wastes tokens on irrelevant content |

Sentence-aware chunking (splitting at sentence boundaries) consistently outperforms fixed-size chunking — it never cuts a sentence in half.

## 2. Contextual Compression

After retrieval, use the LLM to distil each chunk to only the sentences relevant to the current query.

```
Full policy section:  500 tokens
After compression:     60 tokens  (88% reduction, all relevant content kept)
```

## 3. Re-ranking

Score each retrieved chunk for relevance and reorder before passing to the generator. Put the highest-scoring chunk closest to the user query (bottom) to exploit the recency effect.

---

## Hands-On Task

```bash
python code/module4/lesson2_compression.py
```

1. Compare fixed-size vs sentence-aware chunking on the sample document
2. Run contextual compression on 3 chunks — what is the average token reduction?
3. Does the top re-ranked chunk match your manual selection?

---

*Next: [Lesson 3 — Token Budget Management](Lesson3_Token_Budget.md)*
