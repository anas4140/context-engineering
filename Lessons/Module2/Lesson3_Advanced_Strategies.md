# **Module 2, Lesson 3: Advanced Prompt Strategies**

This lesson covers meta-prompting, self-consistency, and prompt chaining — techniques for pushing reliability beyond what a single prompt can achieve.

---

## Learning Objectives

- **Define** prompt chaining and explain when to use it over a single prompt
- **Explain** self-consistency sampling and majority voting
- **Apply** meta-prompting to generate and improve prompts automatically

---

## 1. Prompt Chaining

Break a complex task into a sequence of simpler prompts, where the output of each step feeds into the next.

**When to chain:**
- The task has clearly separable stages (extract → analyse → format)
- Each stage needs different instructions or tone
- You want to inspect or validate intermediate results

**Example chain for a research summary:**
```
Step 1: Extract all factual claims from the document
Step 2: Fact-check each claim against the retrieved knowledge base  
Step 3: Write a summary using only verified claims
Step 4: Format the summary in the required output schema
```

Each step is a separate API call with its own focused system prompt.

## 2. Self-Consistency Sampling

For high-stakes reasoning tasks, call the model multiple times with the same prompt and take the majority answer.

```python
answers = [call_model(prompt) for _ in range(5)]
# Take the most common answer
from collections import Counter
final = Counter(answers).most_common(1)[0][0]
```

**When to use:** Maths, logic, factual Q&A where wrong answers are costly and sampling is cheap relative to errors.

## 3. Meta-Prompting

Use the model to generate or improve prompts.

```python
meta_prompt = (
    "You are a prompt engineering expert. "
    "Improve the following system prompt to be more precise and less ambiguous. "
    f"Original prompt: {original_prompt}\n\n"
    "Return only the improved prompt, no commentary."
)
```

**Use case:** You have a prompt that works 80% of the time. Ask Claude to identify the ambiguity causing the 20% failure cases and rewrite it.

---

## Key Takeaways

- Chain prompts when a task has separable stages that benefit from different instructions
- Self-consistency reduces variance at the cost of more API calls
- Meta-prompting treats prompt improvement as an automatable task
- All three techniques compose well with RAG and agents (Modules 3–5)

---

*You've completed Module 2! Next: [Module 3 — Retrieval-Augmented Generation](../Module3/Lesson1_Introduction_to_RAG.md)*

---

## Hands-On Task

Run the advanced strategies demo:

```bash
python code/module2/lesson3_advanced_strategies.py
```

Then try:

1. **Chain prompting**: Take a topic of your choice and write a 3-step chain: (1) generate 5 ideas, (2) pick the best one, (3) expand it into a paragraph. Can one big prompt do what three chained prompts do?
2. **Self-consistency**: Run the same open-ended question 3 times with `temperature=1`. Do the answers agree? What does this tell you about model uncertainty?
3. **Meta-improvement**: Write a deliberately bad system prompt for a customer support bot. Feed it to the `meta_improve_prompt()` function and compare the before/after. What specific changes did the model make?

---

*Next: [Module 3 — Retrieval-Augmented Generation](../Module3/Lesson1_Introduction_to_RAG.md)*
