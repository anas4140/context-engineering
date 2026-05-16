# **Module 8, Lesson 1: Extended Thinking**

Extended thinking lets Claude reason through a private scratchpad before producing its answer. This lesson explains what it is, when to use it, and how it changes context economics.

---

## Learning Objectives

- **Define** extended thinking and how it differs from chain-of-thought prompting
- **Identify** task types that benefit most from a thinking budget
- **Read** thinking blocks from API responses

---

## 1. What Is Extended Thinking?

Standard Claude: user message → answer.

Extended thinking: user message → [hidden scratchpad of reasoning tokens] → answer.

The scratchpad is **not shown to the user** and is **not part of the conversational context** — it exists purely to improve answer quality. You control how many tokens Claude may spend on reasoning via a `budget_tokens` parameter.

```python
response = client.messages.create(
    model="claude-opus-4-7",
    max_tokens=16000,          # must cover budget + answer
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # scratchpad cap; minimum 1024
    },
    messages=[{"role": "user", "content": "Solve this step-by-step: ..."}]
)
```

---

## 2. Reading the Response

The response `content` list contains **two block types**:

| Block type | Contains | Visible to user? |
|------------|----------|-----------------|
| `thinking`  | Full reasoning trace | No (your app decides) |
| `text`      | Final answer | Yes |

```python
for block in response.content:
    if block.type == "thinking":
        print("=== Scratchpad ===")
        print(block.thinking)
    elif block.type == "text":
        print("=== Answer ===")
        print(block.text)
```

---

## 3. When Extended Thinking Helps

| Task type | Benefit |
|-----------|---------|
| Multi-step maths / proofs | Claude checks intermediate steps |
| Complex code review | Catches subtle bugs via deeper analysis |
| Long legal / contract analysis | Tracks many constraints simultaneously |
| Strategic planning | Explores trade-offs before committing |
| Ambiguous instructions | Reasons through edge cases first |

**Does NOT help (and costs more):**
- Simple factual lookups
- Short creative writing
- Classification with few classes
- Any task where the answer is obvious

---

## 4. Token Economics

```
Total tokens billed = thinking_tokens + output_tokens
max_tokens must be ≥ budget_tokens + expected_output_tokens
```

Thinking tokens are billed at **the same input rate** as the rest of the prompt — but you get dramatically better reasoning for complex tasks. For simple tasks, skip the budget entirely.

---

## 5. Thinking vs. Chain-of-Thought Prompting

| | Extended Thinking | CoT in prompt |
|--|--|--|
| Where reasoning appears | Separate `thinking` block | Inside the visible answer |
| Token budget | Separate, configurable | Shares output budget |
| User sees it | Only if you show `block.thinking` | Always |
| Instruction required | Just `thinking: {type: enabled}` | "Think step by step" in prompt |
| Available on | claude-opus-4-7 | All models |

---

## Key Takeaways

- Extended thinking adds a hidden reasoning scratchpad before the visible answer
- Set `budget_tokens` to control the scratchpad size (min 1024); `max_tokens` must be larger
- Use it for complex, multi-step tasks — skip it for simple ones
- Response blocks come in order: `thinking` first, then `text`

---

*Next: [Lesson 2 — Thinking Budgets & Cost Optimisation](Lesson2_Thinking_Budgets.md)*
