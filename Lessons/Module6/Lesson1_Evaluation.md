# **Module 6, Lesson 1: Evaluation — Measuring What Matters**

You cannot improve what you cannot measure. This lesson builds a practical evaluation suite for RAG systems using the LLM-as-judge pattern.

---

## Learning Objectives

- **Define** faithfulness, answer relevance, and context precision
- **Implement** LLM-as-judge evaluation for each metric
- **Build** a scored evaluation table for any RAG pipeline ([code/module6/lesson1_evaluation.py](../../code/module6/lesson1_evaluation.py))

---

## 1. Why Evaluation is Hard

You can't unit-test an LLM response the way you unit-test a function. The output is natural language — there is no single "correct" answer. Instead, you evaluate along dimensions that matter for your use case.

The three most important RAG dimensions:

| Metric | What fails when it's low |
|---|---|
| **[Faithfulness](../../GLOSSARY.md)** | Model is hallucinating beyond the retrieved context |
| **Answer Relevance** | Model is answering a different question than was asked |
| **Context Precision** | Retriever is fetching irrelevant chunks |

## 2. LLM-as-Judge

Use a second LLM call to score the first. This is scalable, automatable, and correlates well with human judgment on well-designed rubrics.

The key: ask for a **structured JSON response with a score and reasoning**, not a free-text opinion. This makes results parseable and trackable over time.

```python
prompt = """Rate this answer's faithfulness to the context: 0.0 to 1.0.
Context: {context}
Answer: {answer}
Respond with JSON only: {"score": float, "reasoning": "one sentence"}"""
```

## 3. Building a Regression Suite

Once you have evaluation metrics, build a fixed dataset of (question, context, expected_answer) triples. Run this suite every time you change the prompt, chunking strategy, or retrieval parameters. If any score drops, you've regressed.

---

## Hands-On Task

```bash
python code/module6/lesson1_evaluation.py
```

1. Add 2 more test cases to `eval_dataset` — one where the answer is correct and one where it halluccinates
2. Which metric catches hallucination? Which catches off-topic answers?
3. Deliberately break the RAG generator prompt (remove "answer ONLY from context") and re-run. What scores change?

---

*Next: [Lesson 2 — Systematic Testing](Lesson2_Testing.md)*
