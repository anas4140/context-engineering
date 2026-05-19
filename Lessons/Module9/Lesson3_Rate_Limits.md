# **Module 9, Lesson 3: Rate Limits & Retry Logic**

Production applications hit rate limits. This lesson shows how to handle them gracefully with exponential back-off, token-aware request pacing, and circuit breakers.

---

## Learning Objectives

- **Identify** Anthropic rate limit error types
- **Implement** automatic retry with exponential back-off using `tenacity`
- **Design** a token-budget-aware request queue

---

## 1. Rate Limit Error Types

| Error class | HTTP | Meaning |
|-------------|------|---------|
| `RateLimitError` | 429 | Too many requests per minute (RPM) or tokens per minute (TPM) |
| `APIStatusError` | 529 | Anthropic is overloaded — treat like a rate limit |
| `APIConnectionError` | — | Network failure — always retry |
| `APITimeoutError` | — | Request timed out — retry with back-off |

---

## 2. Basic Retry with Tenacity

`tenacity` is already in `requirements.txt`. Wrap any API call:

```python
from tenacity import (
    retry, stop_after_attempt, wait_exponential,
    retry_if_exception_type, before_sleep_log
)
import logging
import anthropic

logger = logging.getLogger(__name__)

@retry(
    retry=retry_if_exception_type((
        anthropic.RateLimitError,
        anthropic.APIConnectionError,
        anthropic.APITimeoutError,
    )),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    stop=stop_after_attempt(6),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
def create_with_retry(client: anthropic.Anthropic, **kwargs):
    return client.messages.create(**kwargs)
```

The decorator:
1. Catches rate limit and network errors
2. Waits 4s → 8s → 16s → 32s → 60s between retries
3. Gives up after 6 attempts and re-raises the exception

---

## 3. Reading Retry-After Headers

When Anthropic returns a 429, the response includes a `Retry-After` header with the exact number of seconds to wait:

```python
import time

def create_respecting_retry_after(client, **kwargs):
    while True:
        try:
            return client.messages.create(**kwargs)
        except anthropic.RateLimitError as e:
            retry_after = int(e.response.headers.get("retry-after", 10))
            print(f"Rate limited. Waiting {retry_after}s...")
            time.sleep(retry_after)
```

Combine this with `tenacity` by checking the header inside the retry callback.

---

## 4. Token-Aware Pacing

TPM limits are often tighter than RPM limits. Estimate tokens before sending:

```python
def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 characters per token for English."""
    return len(text) // 4

TPM_LIMIT   = 40_000
WINDOW_SECS = 60

tokens_used = 0
window_start = time.time()

def paced_create(client, content: str, **kwargs):
    global tokens_used, window_start

    now = time.time()
    if now - window_start >= WINDOW_SECS:    # reset window
        tokens_used  = 0
        window_start = now

    estimated = estimate_tokens(content)
    if tokens_used + estimated > TPM_LIMIT:
        wait = WINDOW_SECS - (now - window_start)
        print(f"Approaching TPM limit. Pacing: waiting {wait:.1f}s")
        time.sleep(wait)
        tokens_used  = 0
        window_start = time.time()

    response = client.messages.create(**kwargs)
    tokens_used += response.usage.input_tokens + response.usage.output_tokens
    return response
```

---

## 5. Headers to Monitor

Every API response includes usage headers:

```python
response = client.messages.create(...)
headers  = response._raw_response.headers      # underlying httpx response

print(headers.get("anthropic-ratelimit-requests-remaining"))
print(headers.get("anthropic-ratelimit-tokens-remaining"))
print(headers.get("anthropic-ratelimit-requests-reset"))
```

Log these in production to alert before you hit limits rather than after.

---

## Key Takeaways

- `RateLimitError` (429) and `APIStatusError` (529) should always be retried
- `tenacity` makes exponential back-off a one-decorator change
- Read `Retry-After` headers for precise wait times
- Estimate tokens before sending to pace requests within TPM limits
- Monitor remaining-quota headers to alert proactively

---

*Up next: Module 10 — Model Context Protocol*

---

## Hands-On Task

```bash
python code/module9/lesson3_rate_limits.py
```

1. **Read quota headers**: After `create_with_retry()` succeeds, print `show_quota_headers(response)`. How many requests remain? Reset happens at what time?
2. **Trigger the retry**: Set `stop_after_attempt(2)` in the tenacity decorator and intentionally send a request with an invalid model name. Does it retry? What's the final exception?
3. **TPM pacing**: Set `TokenPacer(tpm_limit=100)` — a very tight limit. Send a 200-token prompt. Does the pacer wait before sending? Add a print statement to confirm it's pacing correctly.

---

*Next: [Module 10 — Model Context Protocol](../Module10/Lesson1_MCP_Introduction.md)*
