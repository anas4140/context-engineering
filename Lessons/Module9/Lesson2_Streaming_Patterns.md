# **Module 9, Lesson 2: Streaming Patterns**

Streaming delivers tokens as they are generated instead of waiting for the full response. This lesson covers when and how to stream, including tool use and multi-turn agents.

---

## Learning Objectives

- **Implement** basic token streaming with `client.messages.stream()`
- **Handle** streaming tool use events
- **Extract** usage statistics from streamed responses

---

## 1. Basic Text Streaming

```python
with client.messages.stream(
    model="claude-haiku-4-5-20251001",
    max_tokens=512,
    messages=[{"role": "user", "content": "Write a haiku about context windows."}],
) as stream:
    for text in stream.text_stream:        # yields str chunks
        print(text, end="", flush=True)

final = stream.get_final_message()         # full Message object
print(f"\nTotal tokens: {final.usage.input_tokens + final.usage.output_tokens}")
```

`stream.text_stream` is the simplest interface — it yields only text deltas and skips all other event types automatically.

---

## 2. Event-Level Streaming

For full control (e.g., handling tool use or thinking blocks):

```python
with client.messages.stream(...) as stream:
    for event in stream:
        match event.type:
            case "message_start":
                print(f"Input tokens: {event.message.usage.input_tokens}")
            case "content_block_start":
                print(f"\nNew block: {event.content_block.type}")
            case "content_block_delta":
                if hasattr(event.delta, "text"):
                    print(event.delta.text, end="", flush=True)
            case "message_stop":
                print("\nDone.")
```

---

## 3. Streaming Tool Use

Tool use stop reasons still arrive through the stream. Collect the full tool block then execute:

```python
tool_inputs = {}
current_tool_id = None

with client.messages.stream(model=..., tools=TOOLS, messages=messages) as stream:
    for event in stream:
        if event.type == "content_block_start" and event.content_block.type == "tool_use":
            current_tool_id   = event.content_block.id
            tool_inputs[current_tool_id] = {"name": event.content_block.name, "input": ""}
        elif event.type == "content_block_delta" and hasattr(event.delta, "partial_json"):
            if current_tool_id:
                tool_inputs[current_tool_id]["input"] += event.delta.partial_json

    final = stream.get_final_message()

if final.stop_reason == "tool_use":
    for tool_id, tool in tool_inputs.items():
        import json
        parsed_input = json.loads(tool["input"])
        result = execute_tool(tool["name"], parsed_input)
        # Add result to messages and loop...
```

---

## 4. When NOT to Stream

| Scenario | Recommendation |
|----------|---------------|
| Batch/async workloads | Use Batch API instead |
| Server-side processing with no UI | Non-streaming is simpler |
| Short responses (< 100 tokens) | Latency benefit is negligible |
| Saving to a database | Collect full response first |

Streaming shines in user-facing applications where time-to-first-token matters.

---

## 5. Time-to-First-Token Measurement

```python
import time

start = time.time()
first_token_time = None

with client.messages.stream(...) as stream:
    for text in stream.text_stream:
        if first_token_time is None:
            first_token_time = time.time() - start
        print(text, end="", flush=True)

total_time = time.time() - start
print(f"\nTTFT: {first_token_time:.2f}s | Total: {total_time:.2f}s")
```

---

## Key Takeaways

- `stream.text_stream` is the simplest streaming interface for pure text responses
- Use event-level iteration for tool use, thinking blocks, or usage tracking
- Collect partial JSON deltas for tool inputs; parse only when the block is complete
- Measure TTFT to understand perceived latency from the user's perspective

---

*Next: [Lesson 3 — Rate Limits & Retry Logic](Lesson3_Rate_Limits.md)*
