# **Module 7, Lesson 1: Emerging Patterns in Context Engineering**

The field moves fast. This lesson surveys the most impactful patterns emerging in 2024-2025 that extend beyond the core techniques covered in Modules 1-6.

---

## Learning Objectives

- **Define** extended thinking, prompt caching, and structured outputs
- **Explain** how each pattern changes the context engineering workflow
- **Apply** prompt caching to reduce costs on repeated system prompts

---

## 1. Extended Thinking

Claude can be instructed to "think before answering" — generating a scratchpad of reasoning tokens that are not shown to the user but influence the final output. This is different from Chain-of-Thought prompting: the thinking happens in a separate token budget and can be much longer.

**When to use:** Complex multi-step reasoning, maths, code review, or any task where CoT in the visible output would be too verbose for the user.

**Context engineering implication:** Extended thinking consumes a separate token budget. Budget it separately from your context window allocation.

## 2. Prompt Caching

If your system prompt is long (thousands of tokens) and repeated across many requests, Anthropic's prompt caching feature allows the processed prompt to be cached server-side. Subsequent requests that include the same prompt prefix are significantly cheaper and faster.

**When to use:** Any application with a fixed, lengthy system prompt — RAG systems with large static knowledge blocks, agents with long tool definitions, applications with detailed persona prompts.

```python
# Mark content for caching with cache_control
system = [
    {
        "type": "text",
        "text": long_system_prompt,
        "cache_control": {"type": "ephemeral"}  # Cache this block
    }
]
```

## 3. Structured Outputs

Rather than asking Claude to format its response in JSON and parsing the result (which can fail), newer API features allow you to specify a JSON schema that the output must conform to. The model is constrained to produce valid JSON matching your schema.

**Context engineering implication:** Structured outputs replace the need for detailed formatting instructions in Layer 10. The schema *is* the format instruction.

---

## Key Takeaways

- Extended thinking separates scratchpad reasoning from user-visible output
- Prompt caching reduces cost and latency for applications with stable system prompts
- Structured outputs replace fragile JSON parsing with schema-constrained generation
- All three patterns are additive — they work alongside everything from Modules 1-6

---

*Next: [Lesson 2 — Multimodal Context](Lesson2_Multimodal.md)*
