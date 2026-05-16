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
