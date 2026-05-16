# **Module 2, Lesson 2: Prompting Techniques in Practice**

This lesson puts five core techniques into runnable code. Every example is executable and directly comparable.

---

## Learning Objectives

- **Build** working examples of zero-shot, few-shot, CoT, XML-structured, and role prompting
- **Compare** outputs from different techniques on the same task
- **Apply** few-shot formatting to classification and extraction tasks

---

## 1. Zero-Shot

No examples, no special instructions — just the task.

**Best for:** Translation, summarisation, simple Q&A, tasks the model sees constantly in training.

**Weakness:** Inconsistent output format. If you need a specific structure, the model will invent its own.

## 2. Few-Shot

2–5 worked examples before the real task, formatted as alternating user/assistant messages.

**Best for:** Classification tasks (sentiment, category, priority), extraction with a fixed schema, any task where the output format must be exactly right.

**Key insight:** The examples teach format, not facts. The model already knows how to classify sentiment — the examples tell it *how to express* the classification.

## 3. Chain-of-Thought (CoT)

Add "think step by step" or show worked reasoning examples before the final answer.

**Best for:** Maths, logic puzzles, multi-step reasoning, tasks where the final answer depends on intermediate calculations.

**Why it works:** CoT forces the model to commit to intermediate steps in the output, reducing the chance of a plausible-but-wrong shortcut.

## 4. XML-Structured Prompting

Wrap different content types in XML tags to separate instructions from data.

**Best for:** Any prompt that mixes your instructions with user-provided content, documents, or retrieved chunks.

**Why it matters:** This is also a security technique — it prevents prompt injection by treating tagged content as data rather than instructions.

## 5. Role Prompting

Define a persona in the system prompt. The model "becomes" that expert.

**Best for:** Domain-specific advice (medical, legal, financial, engineering), tone matching, creative writing with a defined voice.

**Limitation:** Role prompting improves style and terminology but doesn't give the model knowledge it wasn't trained on. For domain-specific facts, combine with RAG (Module 3).

---

## Hands-On Task

Run the full demo:

```bash
python code/module2/lesson2_prompting_techniques.py
```

Then:

1. Add a fourth sentiment label (`"COMPLAINT"`) to the few-shot classifier. What minimum examples does it need?
2. Try removing "think step by step" from the CoT prompt. How does accuracy change on the word problem?
3. Write a role prompt for a `"senior Python engineer"` and ask it to review a 5-line function. Compare to the same question without a role.

---

*Next: [Lesson 3 — Advanced Prompt Strategies](Lesson3_Advanced_Strategies.md)*
