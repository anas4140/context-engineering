# **Module 9, Lesson 1: The Message Batches API**

The Batches API lets you submit hundreds of requests at once, process them asynchronously, and retrieve results when ready — at **50% lower cost** than synchronous calls. It's the right tool for evaluation runs, dataset annotation, and any workload that doesn't need an immediate answer.

---

## Learning Objectives

- **Explain** when to prefer batch over synchronous API calls
- **Create** a batch request and poll for completion
- **Process** batch results and handle partial failures

---

## 1. When to Use Batching

| Use case | Sync API | Batch API |
|----------|----------|-----------|
| Interactive chat | ✓ | — |
| Evaluation suite (100+ test cases) | slow + expensive | ✓ |
| Dataset annotation | very expensive | ✓ |
| Nightly report generation | wastes daytime rate limit | ✓ |
| One-off queries | ✓ | overkill |

Rule of thumb: if you can wait **up to 24 hours** and have **more than ~10 requests**, use the Batch API.

---

## 2. Creating a Batch

```python
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": "eval-001",        # your ID — returned with results
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 256,
                "messages": [{"role": "user", "content": "Is 'The sky is green' true?"}],
            },
        },
        {
            "custom_id": "eval-002",
            "params": {
                "model": "claude-haiku-4-5-20251001",
                "max_tokens": 256,
                "messages": [{"role": "user", "content": "Capital of Japan?"}],
            },
        },
    ]
)
print(batch.id)                   # batch_01abc...
print(batch.processing_status)    # "in_progress"
```

---

## 3. Polling for Completion

```python
import time

while batch.processing_status == "in_progress":
    time.sleep(10)
    batch = client.messages.batches.retrieve(batch.id)
    print(f"Status: {batch.processing_status} | "
          f"Succeeded: {batch.request_counts.succeeded} | "
          f"Errored: {batch.request_counts.errored}")
```

Batches complete in minutes for small jobs, up to 24 hours for large ones. Typical small batches (<100 requests) finish in 1–5 minutes.

---

## 4. Retrieving Results

```python
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        text = result.result.message.content[0].text
        print(f"{result.custom_id}: {text[:80]}")
    elif result.result.type == "errored":
        print(f"{result.custom_id}: ERROR — {result.result.error.type}")
```

Results are streamed — you don't need to load all of them into memory at once.

---

## 5. Cost Calculation

Batch requests are billed at **50% of the standard per-token rate**. For large evaluation suites:

```
Standard: 100 cases × 500 tokens each = 50,000 tokens @ $0.25/MTok = $0.0125
Batch:    same                                              @ $0.125/MTok = $0.00625
Saving:   50%
```

At scale (1M tokens/day for eval), batch pricing saves ~$45/day.

---

## Key Takeaways

- The Batch API is 50% cheaper and designed for async, non-interactive workloads
- Submit with `custom_id` tags so results map back to your test cases
- Poll `processing_status` until `"ended"`; then stream results with `.results()`
- Handle `errored` results gracefully — partial failures are normal

---

*Next: [Lesson 2 — Streaming Patterns](Lesson2_Streaming_Patterns.md)*

---

## Hands-On Task

```bash
python code/module9/lesson1_batch_api.py
```

1. **Scale it up**: Add 10 more test cases to `TEST_CASES`. Submit all 20 as a single batch. Does the wall-clock time stay roughly constant (proving async processing)?
2. **Cost calculation**: After the batch completes, calculate the total input + output tokens from the results. What would this have cost at standard pricing? What did it cost at batch pricing (50% off)?
3. **Handle errors gracefully**: Deliberately add a malformed request to the batch (e.g., `"max_tokens": -1`). Check what `result.result.type` is for that item and print the error message.

---

*Next: [Lesson 2 — Streaming Patterns](Lesson2_Streaming_Patterns.md)*
