# **Module 11, Lesson 1: Async Basics with AsyncAnthropic**

Synchronous code calls the API and waits. Async code fires multiple calls concurrently and collects results when they're ready — often 3-10× faster for independent queries.

---

## Learning Objectives

- **Explain** why async matters for multi-query AI applications
- **Use** `anthropic.AsyncAnthropic` with `async/await`
- **Measure** the wall-clock speedup of concurrent vs. sequential calls

---

## 1. The Problem with Sequential Calls

```python
# Sequential: each call waits for the previous to finish
# 4 queries × 1.5s each = ~6 seconds total
for query in queries:
    result = client.messages.create(...)   # blocks here
```

Each call blocks the thread. For independent queries, this wastes time.

---

## 2. AsyncAnthropic

Drop-in async replacement for the synchronous client:

```python
import asyncio
import anthropic

# Sync client
client = anthropic.Anthropic()

# Async client — same API, all methods are awaitable
async_client = anthropic.AsyncAnthropic()

async def ask(prompt: str) -> str:
    response = await async_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
```

---

## 3. Concurrent Queries with asyncio.gather

```python
async def run_all(prompts: list[str]) -> list[str]:
    # Fire all calls at once — total time ≈ slowest single call
    return await asyncio.gather(*[ask(p) for p in prompts])

results = asyncio.run(run_all(prompts))
```

`asyncio.gather` runs all coroutines concurrently. For 4 × 1.5s queries, total time drops from ~6s to ~1.5s.

---

## 4. Async Streaming

Streaming works the same way with `async for`:

```python
async def stream_response(prompt: str):
    async with async_client.messages.stream(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:
            print(text, end="", flush=True)
```

---

## 5. Rate-Limit-Safe Concurrency with Semaphores

Firing 100 requests simultaneously will hit rate limits. Use `asyncio.Semaphore` to cap concurrency:

```python
SEM = asyncio.Semaphore(5)   # max 5 in-flight at once

async def ask_safe(prompt: str) -> str:
    async with SEM:
        return await ask(prompt)

results = await asyncio.gather(*[ask_safe(p) for p in 100_prompts])
```

---

## Key Takeaways

- `AsyncAnthropic` is the async client — same methods, all awaitable
- `asyncio.gather()` runs independent calls concurrently — total time ≈ slowest single call
- `asyncio.Semaphore(N)` caps concurrency to avoid rate limits
- Async streaming uses `async with` and `async for`

---

*Next: [Lesson 2 — Concurrent Multi-Agent Systems](Lesson2_Concurrent_Agents.md)*

---

## Hands-On Task

```bash
python code/module11/lesson1_async_basics.py
```

1. **Measure the speedup**: Change `QUERIES` to contain 8 items. Run both sequential and concurrent versions. Calculate the speedup ratio. Does it scale linearly with the number of queries?
2. **Semaphore effect**: Change `max_concurrency=3` to `max_concurrency=1`. Does it behave like the sequential version? Change it to `max_concurrency=10`. What happens if you exceed your rate limit?
3. **Async streaming**: Modify `stream_response()` to also record and print the time-to-first-token. Does async streaming have lower TTFT than a regular `await async_client.messages.create()`?

---

*Next: [Lesson 2 — Concurrent Multi-Agent Systems](Lesson2_Concurrent_Agents.md)*
