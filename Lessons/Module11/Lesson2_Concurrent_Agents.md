# **Module 11, Lesson 2: Concurrent Multi-Agent Systems**

Async unlocks true parallelism for multi-agent workflows. This lesson applies `asyncio` to the orchestrator-subagent pattern — running independent subagents simultaneously instead of sequentially.

---

## Learning Objectives

- **Design** an async orchestrator that runs subagents in parallel
- **Handle** errors and timeouts in concurrent agent calls
- **Implement** an async evaluation pipeline

---

## 1. Sequential vs. Parallel Orchestration

```
Sequential (Module 5 style):
  Orchestrator → Researcher (2s) → Writer (2s) → Critic (2s) = 6s total

Parallel (this lesson):
  Orchestrator → [Researcher + Writer + Critic running at once] = ~2s total
```

When subagents don't depend on each other's output, run them in parallel.

---

## 2. Async Orchestrator Pattern

```python
import asyncio
import anthropic

async_client = anthropic.AsyncAnthropic()

async def subagent(system: str, task: str) -> str:
    """Single-purpose async agent."""
    response = await async_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        system=system,
        messages=[{"role": "user", "content": task}],
    )
    return response.content[0].text

async def parallel_research(topic: str) -> dict:
    """Run three specialised researchers concurrently."""
    facts, pros, cons = await asyncio.gather(
        subagent("You are a fact researcher.",      f"List 3 key facts about: {topic}"),
        subagent("You are a benefits analyst.",     f"List 3 benefits of: {topic}"),
        subagent("You are a risk analyst.",         f"List 3 risks of: {topic}"),
    )
    return {"facts": facts, "pros": pros, "cons": cons}
```

---

## 3. Error Handling in Concurrent Calls

`asyncio.gather` raises the first exception by default. Use `return_exceptions=True` to collect all results including errors:

```python
results = await asyncio.gather(
    *[subagent(system, task) for system, task in agent_tasks],
    return_exceptions=True,
)

for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Agent {i} failed: {result}")
    else:
        print(f"Agent {i}: {result}")
```

---

## 4. Timeouts

```python
async def ask_with_timeout(prompt: str, timeout: float = 30.0) -> str:
    try:
        return await asyncio.wait_for(ask(prompt), timeout=timeout)
    except asyncio.TimeoutError:
        return "Agent timed out — using fallback."
```

---

## 5. Async Evaluation Pipeline

Run all evaluation metrics concurrently instead of sequentially:

```python
async def evaluate_all(answer: str, context: str, question: str) -> dict:
    faithfulness, relevance, precision = await asyncio.gather(
        score("faithfulness", answer, context),
        score("relevance",    answer, question),
        score("precision",    context, question),
    )
    return {"faithfulness": faithfulness, "relevance": relevance, "precision": precision}
```

This replaces 3 sequential API calls (~4.5s) with 1 concurrent batch (~1.5s).

---

## Key Takeaways

- Run independent subagents with `asyncio.gather` — wall time ≈ slowest single agent
- Use `return_exceptions=True` to handle partial failures gracefully
- `asyncio.wait_for` adds per-call timeouts
- Async evaluation pipelines are 3-5× faster than sequential scoring

---

*Up next: Module 12 — Prompt Versioning & A/B Testing*

---

## Hands-On Task

```bash
python code/module11/lesson2_concurrent_agents.py
```

1. **Time the parallel vs sequential**: Copy the `parallel_research()` function and create a `sequential_research()` version that uses `await` on each subagent one at a time. Measure the wall-clock time difference on the same topic.
2. **Partial failure recovery**: Change one of the subagent calls to use `timeout=0.001` (guaranteed timeout). Use `gather_with_fallbacks()` to collect results. Does the synthesiser still produce a useful answer with one missing input?
3. **Parallel evaluation**: Use `asyncio.gather` to run `evaluate_parallel()` on 3 different answers simultaneously. How long does scoring 3 answers take vs scoring them one at a time?

---

*Next: [Module 12 — Prompt Versioning & A/B Testing](../Module12/Lesson1_Prompt_Versioning.md)*
