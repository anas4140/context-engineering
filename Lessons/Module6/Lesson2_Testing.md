# **Module 6, Lesson 2: Systematic Testing**

Evaluation tells you what quality is. Testing tells you when quality has changed. This lesson builds a repeatable test harness for context-aware AI systems.

---

## Learning Objectives

- **Define** the difference between evaluation (absolute quality) and testing (regression detection)
- **Build** a parametrised test suite using pytest
- **Apply** snapshot testing to detect prompt regressions

---

## 1. Evaluation vs Testing

| | Evaluation | Testing |
|---|---|---|
| **Question** | How good is this? | Did this get worse? |
| **Output** | Scores (0.0–1.0) | Pass / Fail |
| **When to run** | When building/tuning | On every code change |
| **Comparison** | Against a rubric | Against a baseline snapshot |

Both are necessary. Evaluation finds absolute weaknesses. Testing catches regressions — when a prompt change that was meant to fix one thing silently breaks another.

## 2. Pytest for LLM Testing

Structure tests around behaviours, not exact outputs:

```python
# tests/test_rag.py
import pytest
from code.module3.lesson1_rag_pipeline import ask, build_knowledge_base

@pytest.fixture(scope="module")
def collection():
    return build_knowledge_base(SAMPLE_DOCUMENTS)

def test_pto_question_contains_20_days(collection):
    result = ask("How many PTO days do I get?", collection)
    assert "20" in result["answer"], "Answer should mention 20 PTO days"

def test_out_of_scope_returns_fallback(collection):
    result = ask("What is the capital of France?", collection)
    assert "don't have" in result["answer"].lower() or \
           "not found" in result["answer"].lower(), \
           "Out-of-scope query should trigger fallback"

def test_answer_cites_source(collection):
    result = ask("What is the remote work policy?", collection)
    assert "employee_handbook" in result["answer"].lower(), \
           "Answer should cite the source document"
```

## 3. What to Test

For RAG systems, test these behavioural properties:

- **Factual accuracy** — key numbers and dates appear in answers to known questions
- **Fallback behaviour** — out-of-scope queries return "I don't know", not hallucinated answers
- **Citation presence** — source document names appear in answers
- **Format compliance** — output matches the required structure (JSON, Markdown, etc.)
- **Injection resistance** — malicious inputs don't cause policy violations

---

## Hands-On Task

Create `tests/test_rag_pipeline.py` with at least 5 pytest test cases covering the behaviours above. Run with:

```bash
pip install pytest
pytest tests/ -v
```

All 5 tests should pass against the reference implementation.

---

*Next: [Lesson 3 — Security for Context-Aware Systems](Lesson3_Security.md)*
