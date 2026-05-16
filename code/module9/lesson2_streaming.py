"""
Module 9, Lesson 2: Streaming Patterns
=======================================
Demonstrates three streaming patterns:
  1. Simple text streaming with time-to-first-token measurement
  2. Event-level streaming for full control
  3. Streaming alongside tool use (partial JSON accumulation)

Run:
    python code/module9/lesson2_streaming.py
"""

import os
import sys
import json
import time
import math
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.rule import Rule

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
client  = Anthropic()
console = Console()

CALCULATOR_TOOL = {
    "name": "calculator",
    "description": "Evaluates a Python math expression.",
    "input_schema": {
        "type": "object",
        "properties": {
            "expression": {"type": "string", "description": "Math expression, e.g. 'sqrt(144)'"}
        },
        "required": ["expression"],
    },
}


def calculator(expression: str) -> str:
    allowed = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    allowed["abs"] = abs
    try:
        return f"Result: {eval(expression, {'__builtins__': {}}, allowed)}"
    except Exception as e:
        return f"Error: {e}"


# ─────────────────────────────────────────────
#  Pattern 1: Simple text streaming
# ─────────────────────────────────────────────
def demo_text_stream():
    console.print(Rule("Pattern 1: Text streaming with TTFT measurement"))
    prompt = "Explain how transformer attention works in exactly 5 bullet points."

    start = time.perf_counter()
    first_token_at = None

    with client.messages.stream(
        model=MODEL_FAST,
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            if first_token_at is None:
                first_token_at = time.perf_counter() - start
            console.print(text, end="", markup=False)

        final = stream.get_final_message()

    total = time.perf_counter() - start
    console.print(
        f"\n\n[dim]TTFT: {first_token_at:.2f}s | Total: {total:.2f}s | "
        f"Tokens: {final.usage.input_tokens + final.usage.output_tokens}[/dim]"
    )


# ─────────────────────────────────────────────
#  Pattern 2: Event-level streaming
# ─────────────────────────────────────────────
def demo_event_stream():
    console.print(Rule("Pattern 2: Event-level streaming"))

    with client.messages.stream(
        model=MODEL_FAST,
        max_tokens=256,
        messages=[{"role": "user", "content": "Name three famous physicists and one discovery each."}],
    ) as stream:
        block_count = 0
        for event in stream:
            event_type = getattr(event, "type", None)
            if event_type == "message_start":
                console.print(f"[dim]← message_start (input tokens: {event.message.usage.input_tokens})[/dim]")
            elif event_type == "content_block_start":
                block_count += 1
                console.print(f"[dim]← block_start #{block_count} type={event.content_block.type}[/dim]")
            elif event_type == "content_block_delta" and hasattr(event.delta, "text"):
                console.print(event.delta.text, end="", markup=False)
            elif event_type == "message_stop":
                console.print(f"\n[dim]← message_stop[/dim]")


# ─────────────────────────────────────────────
#  Pattern 3: Streaming with tool use
# ─────────────────────────────────────────────
def demo_tool_stream():
    console.print(Rule("Pattern 3: Streaming tool use"))
    messages = [{"role": "user", "content": "What is sin(45 degrees) times 100, rounded to 2 decimals?"}]

    tool_inputs: dict[str, dict] = {}
    current_tool_id = None

    with client.messages.stream(
        model=MODEL_FAST,
        max_tokens=512,
        tools=[CALCULATOR_TOOL],
        messages=messages,
    ) as stream:
        for event in stream:
            event_type = getattr(event, "type", None)
            if event_type == "content_block_start":
                block = event.content_block
                if block.type == "tool_use":
                    current_tool_id = block.id
                    tool_inputs[current_tool_id] = {"name": block.name, "json": ""}
                    console.print(f"[cyan]Tool call starting: {block.name}[/cyan]")
            elif event_type == "content_block_delta":
                delta = event.delta
                if current_tool_id and hasattr(delta, "partial_json"):
                    tool_inputs[current_tool_id]["json"] += delta.partial_json
                elif hasattr(delta, "text"):
                    console.print(delta.text, end="", markup=False)
        final = stream.get_final_message()

    if final.stop_reason == "tool_use":
        messages.append({"role": "assistant", "content": final.content})
        tool_results = []
        for tid, tool in tool_inputs.items():
            parsed = json.loads(tool["json"]) if tool["json"] else {}
            result = calculator(**parsed)
            console.print(f"[dim]  {tool['name']}({parsed}) → {result}[/dim]")
            tool_results.append({"type": "tool_result", "tool_use_id": tid, "content": result})
        messages.append({"role": "user", "content": tool_results})

        # Final answer (non-streaming for brevity)
        final2 = client.messages.create(model=MODEL_FAST, max_tokens=256, tools=[CALCULATOR_TOOL], messages=messages)
        console.print(f"\n[green]Answer:[/green] {final2.content[0].text}")


if __name__ == "__main__":
    console.print("\n[bold]Module 9, Lesson 2 — Streaming Patterns[/bold]\n")
    demo_text_stream()
    console.print()
    demo_event_stream()
    console.print()
    demo_tool_stream()
    console.print("\n[bold green]✓ Lesson 2 complete![/bold green]")
    console.print("Next: [italic]python code/module9/lesson3_rate_limits.py[/italic]\n")
