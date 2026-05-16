# **Module 3, Lesson 3: Evaluating RAG Quality**

A RAG pipeline that produces wrong answers confidently is worse than one that admits uncertainty. This lesson introduces the metrics that tell you whether your retrieval is actually helping.

---

## Learning Objectives

- **Define** faithfulness, answer relevance, and context precision
- **Explain** how LLM-as-judge evaluation works
- **Apply** the three metrics to identify weaknesses in a RAG pipeline

---

## 1. The Three Core RAG Metrics

| Metric | Question it answers | What low score means |
|---|---|---|
| **Faithfulness** | Does the answer stick to the retrieved context? | The model is hallucinating |
| **Answer Relevance** | Does the answer address the question? | The generation is off-topic |
| **Context Precision** | Is the retrieved context actually relevant? | The retriever is fetching wrong chunks |

## 2. Faithfulness — The Most Important Metric

Faithfulness measures whether every factual claim in the generated answer is supported by the retrieved context. A score of 1.0 means every claim has a source. A score of 0.5 means half the claims are invented.

**A faithfulness failure is a hallucination.** The model made up something that wasn't in the context. This is the primary failure mode RAG is supposed to prevent — but a badly designed generator prompt can still hallucinate even with good context.

**Fix low faithfulness by:**
- Adding explicit "answer ONLY from the context" instructions to the generator prompt
- Adding "if the answer is not in the context, say so" as a rule
- Reducing `max_tokens` to prevent the model from rambling beyond the context

## 3. Context Precision — The Retriever's Report Card

A context precision of 0.3 means 70% of the tokens you retrieved were irrelevant. This wastes context window space and can confuse the generator.

**Fix low context precision by:**
- Reducing `top_k` (retrieve fewer chunks)
- Using metadata filtering to narrow the search space
- Improving chunk quality (better splitting, more coherent chunks)

---

## Hands-On Task

The evaluation code is in Module 6, Lesson 1. For now:

1. Run the basic RAG pipeline from Lesson 1 with 5 test questions
2. For each response, manually score faithfulness (0/0.5/1) — does every claim appear in the retrieved context?
3. Which question had the lowest faithfulness? Why?

---

*Next: [Lesson 4 — Production RAG Patterns](Lesson4_Production_RAG.md)*

---

# **Module 3, Lesson 4: Production RAG Patterns**

This lesson covers the architectural patterns used in production RAG systems — going beyond the basic pipeline to handle scale, accuracy, and maintainability.

---

## Learning Objectives

- **Define** the corrective RAG and self-RAG patterns
- **Explain** how query routing enables multi-source RAG
- **Apply** the appropriate pattern for a given production use case

---

## 1. Corrective RAG

After generation, run a faithfulness check. If the score is below a threshold, either retrieve again with a refined query or fall back to a "I don't have enough information" response.

```
Query → Retrieve → Generate → Evaluate Faithfulness
  ↑                                        |
  └──── Re-retrieve with refined query ←──┘ (if score < 0.7)
```

This adds latency but significantly reduces hallucination rates in high-stakes applications.

## 2. Self-RAG

The model itself decides whether to retrieve. Instead of always fetching context, a `retrieve: yes/no` classification runs first. For simple, factual queries the model already knows the answer — retrieval is skipped. For knowledge-intensive queries, retrieval is triggered.

**Benefit:** Reduces cost and latency for queries that don't need retrieval.

## 3. Query Routing

Different query types are served by different retrieval sources:

```
User query → Router → "policy question"  → HR vector store
                    → "product question" → Product catalogue
                    → "support question" → Ticket history
                    → "general question" → Web search
```

The router is either a classifier (faster, cheaper) or another LLM call (more flexible).

---

## Key Takeaways

- Corrective RAG catches hallucinations before they reach the user
- Self-RAG reduces unnecessary retrieval calls
- Query routing enables a single agent to use multiple knowledge sources
- All three patterns compose — production systems often use all three

---

*You've completed Module 3! Next: [Module 4 — Optimising the Context Window](../Module4/Lesson1_Context_Window_Anatomy.md)*
