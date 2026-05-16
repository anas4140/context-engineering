# **Module 8, Lesson 2: Thinking Budgets & Cost Optimisation**

A larger thinking budget is not always better. This lesson shows how to choose the right budget for each task type and how to measure whether the extra tokens are earning their cost.

---

## Learning Objectives

- **Choose** an appropriate thinking budget for different task types
- **Measure** whether extended thinking improved answer quality
- **Implement** an adaptive budget strategy

---

## 1. Budget Tiers

| Budget | Use case | Typical cost multiplier |
|--------|----------|------------------------|
| 1,024 – 2,000 | Light reasoning, classification with justification | 1.2× |
| 2,000 – 5,000 | Code review, short proofs, contract clauses | 1.5× |
| 5,000 – 10,000 | Multi-step maths, complex debugging | 2–3× |
| 10,000 – 32,000 | Research synthesis, full architecture review | 4–8× |

Start at the lowest tier that produces correct answers for your task, not the highest.

---

## 2. Adaptive Budget Strategy

Run the same query at increasing budgets and stop when quality plateaus:

```python
def find_optimal_budget(query: str, budgets: list[int]) -> dict:
    results = {}
    for budget in budgets:
        response = client.messages.create(
            model="claude-opus-4-7",
            max_tokens=budget + 2000,
            thinking={"type": "enabled", "budget_tokens": budget},
            messages=[{"role": "user", "content": query}]
        )
        answer = next(b.text for b in response.content if b.type == "text")
        thinking_used = next(
            (len(b.thinking) for b in response.content if b.type == "thinking"), 0
        )
        results[budget] = {
            "answer": answer,
            "thinking_chars": thinking_used,
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
        }
    return results
```

---

## 3. Thinking Saturation

Claude won't always use its full budget. If the actual thinking block is much shorter than `budget_tokens`, the task doesn't need more reasoning — lower the budget.

```python
thinking_block = next(b for b in response.content if b.type == "thinking")
utilisation = len(thinking_block.thinking) / budget_tokens
if utilisation < 0.5:
    print("Budget oversized — halve it next time")
```

---

## 4. Streaming with Extended Thinking

When streaming, thinking blocks arrive as `content_block_start` events with type `thinking`:

```python
with client.messages.stream(
    model="claude-opus-4-7",
    max_tokens=12000,
    thinking={"type": "enabled", "budget_tokens": 8000},
    messages=[{"role": "user", "content": query}],
) as stream:
    current_block_type = None
    for event in stream:
        if hasattr(event, "type"):
            if event.type == "content_block_start":
                current_block_type = event.content_block.type
            elif event.type == "content_block_delta":
                if current_block_type == "thinking" and hasattr(event.delta, "thinking"):
                    print(event.delta.thinking, end="", flush=True)
                elif current_block_type == "text" and hasattr(event.delta, "text"):
                    print(event.delta.text, end="", flush=True)
```

---

## 5. Thinking in Multi-Turn Conversations

To maintain reasoning continuity across turns, pass the full `content` list (including thinking blocks) back as assistant messages:

```python
messages = [{"role": "user", "content": "Start a complex analysis..."}]

response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=12000,
    thinking={"type": "enabled", "budget_tokens": 8000},
    messages=messages,
)

# Include the thinking block in history so follow-up turns stay coherent
messages.append({"role": "assistant", "content": response.content})
messages.append({"role": "user", "content": "Now extend that analysis..."})
```

---

## Key Takeaways

- Start with the smallest budget that produces correct answers; grow only if needed
- Check thinking utilisation — if Claude uses < 50% of the budget, the budget is too large
- Thinking blocks can be streamed and included in multi-turn history
- The right budget varies by task type, not by a fixed rule

---

*Up next: Module 9 — Production at Scale*
