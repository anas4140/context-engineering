# **Module 4, Lesson 3: Token Budget Management**

Multi-turn conversations accumulate history that grows every turn. Without management, you will eventually overflow the context window. This lesson teaches you to manage that budget proactively.

---

## Learning Objectives

- **Implement** a token counter that tracks usage across a conversation
- **Apply** a sliding window strategy to keep history within budget
- **Build** a conversation summariser that compresses history before overflow

---

## 1. The Running Budget Problem

Track tokens actively and act before the limit is hit:

```python
BUDGET = 180_000  # Leave 20K for output
used   = count_tokens(system_prompt)
used  += sum(count_tokens(m["content"]) for m in history)
used  += count_tokens(rag_context)

if used > BUDGET * 0.8:   # Act at 80%, not 100%
    history = summarise_and_compress(history)
```

## 2. Sliding Window vs Summarisation

| Strategy | How it works | What is lost |
|---|---|---|
| **Sliding window** | Keep last N turns, discard the rest | All early context |
| **Summarisation** | Compress old turns into a 3-sentence summary | Minor details |

Summarisation is always preferable when latency allows — it preserves semantic content that the sliding window discards entirely.

## 3. The 80% Trigger

Act at 80% capacity, not 100%. At 100% the API will either error or silently truncate from the beginning — losing your system prompt. The Final Project's `research_assistant.py` implements this pattern.

---

## Key Takeaways

- Track token usage proactively across every turn
- Summarise history at 80% capacity — don't wait for an error
- Always reserve at least 10-20% of the budget for model output
- Sliding window is simpler; summarisation preserves more context

---

*You've completed Module 4! Next: [Module 5 — From RAG to Agents](../Module5/Lesson1_ReAct_Pattern.md)*

---

## Hands-On Task

```bash
python code/module4/lesson3_token_budget.py
```

1. Set `MAX_TOKENS = 500` in the demo. At what turn does the budget-aware conversation start compressing history?
2. The `compress_history()` function keeps the most recent 4 turns. Change it to keep the most recent 2 turns. How does answer quality change on turn 10?
3. Implement a `token_warning()` function that prints a warning when the context window is over 80% full.

---

*Next: [Module 5 — From RAG to Agents](../Module5/Lesson1_ReAct_Pattern.md)*
