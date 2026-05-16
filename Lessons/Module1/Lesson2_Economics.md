# **Module 1, Lesson 2: The Economics of Context — Tokens and Cost**

Every character you send to an LLM costs money and consumes a finite resource: the context window. This lesson teaches you to think about context as a budget to be spent wisely.

---

## Learning Objectives

- **Define** a token and explain the relationship between tokens, cost, and context window size
- **Explain** how system prompt length affects cost at scale
- **Apply** token counting to estimate API costs before deployment
- **Build** a cost comparison tool ([code/module1/lesson2_economics.py](../../code/module1/lesson2_economics.py))

---

## 1. What is a Token?

LLMs don't process text character by character — they process **tokens**, which are chunks of text that a tokeniser has split the input into.

Rule of thumb:
- **1 token ≈ 4 characters** in English
- **1 token ≈ 0.75 words**
- "Hello, world!" → 4 tokens
- A typical paragraph → 60–80 tokens
- This entire lesson → approximately 800 tokens

Tokens are the unit of measurement for:
- **Pricing** (cost per million tokens)
- **Context window size** (maximum tokens per request)
- **Rate limits** (tokens per minute)

---

## 2. Input vs Output Tokens

Every API call has two token counts:

| Token type | What counts | Typical cost ratio |
|---|---|---|
| **Input** | System prompt + history + retrieved docs + user message | 1× |
| **Output** | The model's response | 3–5× more expensive |

Output tokens cost more because generating text is computationally heavier than reading it. This means verbose system prompts are relatively cheap — what's expensive is asking for long responses.

---

## 3. The Scale Problem

A padded system prompt that wastes 200 tokens feels trivial for a single call. At production scale:

| Daily requests | Extra tokens/call | Extra tokens/month | Cost (Haiku) |
|---|---|---|---|
| 1,000 | 200 | 6M | ~$4.80 |
| 100,000 | 200 | 600M | ~$480 |
| 1,000,000 | 200 | 6B | ~$4,800 |

Efficient prompts compound into significant savings. See the live calculation in the code.

---

## 4. Context Window Limits

Each Claude model has a maximum context window:

| Model | Context window |
|---|---|
| claude-haiku-4-5 | 200K tokens |
| claude-sonnet-4-6 | 200K tokens |
| claude-opus-4-6 | 200K tokens |

200K tokens sounds large, but a full RAG pipeline consuming system prompt + history + retrieved chunks + response can burn through thousands of tokens per turn in long sessions. Module 4 covers strategies for staying within budget.

---

## 5. Practical Token Budgeting

A simple mental model for allocating the context window:

```
Total budget: 200,000 tokens
├── System prompt (Layer 1-3, 5, 7, 10):     500–2,000 tokens
├── Conversation history (Layer 6):         1,000–10,000 tokens
├── Retrieved knowledge (Layer 8):          500–3,000 tokens
├── Tool definitions (Layer 7):             200–1,000 tokens
└── Reserve for output (Layer 11 response): 512–4,096 tokens
```

For most applications you'll use under 10K tokens per call — well within limits. The constraint becomes relevant in document analysis, long research sessions, or agents that accumulate many tool results.

---

## Key Takeaways

- 1 token ≈ 4 characters ≈ 0.75 words
- Input tokens cost less than output tokens (roughly 3–5× difference)
- Prompt inefficiency compounds at scale into real money
- Use `tiktoken` or the `usage` field in API responses to measure actual token counts
- Budget your context window intentionally, especially for agentic applications

---

## Hands-On Task

Run the economics demo:

```bash
python code/module1/lesson2_economics.py
```

Then:

1. Add a 4th prompt style (`"Ultra-minimal"`) to the `PROMPTS` dict that reduces the medium prompt to under 10 tokens while still being usable
2. Change the production estimate to 10,000 daily requests. At what monthly volume does it become worth spending 1 hour optimising the prompt?
3. Look at the `estimate_cost()` function. Update the prices for `claude-sonnet-4-6` (check the current rates at [anthropic.com/pricing](https://www.anthropic.com/pricing))

---

*Next: [Lesson 3 — Core Principles of Context Engineering](Lesson3_Principles.md)*
