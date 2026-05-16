"""
Module 5, Lesson 3: Structured Outputs
=======================================
Shows how to use tool_choice to force Claude to return validated JSON
that conforms to a schema — no string parsing, no format instructions needed.

Run:
    python code/module5/lesson3_structured_outputs.py
"""

import os
import sys
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
client  = Anthropic()
console = Console()


# ─────────────────────────────────────────────
#  Schema definitions (the "tools")
# ─────────────────────────────────────────────
PERSON_TOOL = {
    "name": "extract_person",
    "description": "Extracts structured person data from unstructured text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name":  {"type": "string",  "description": "Full name"},
            "age":   {"type": "integer", "description": "Age in years"},
            "city":  {"type": "string",  "description": "City of residence"},
            "email": {"type": "string",  "description": "Email address if mentioned"},
        },
        "required": ["name", "age", "city"],
    },
}

SENTIMENT_TOOL = {
    "name": "classify_sentiment",
    "description": "Classifies the sentiment of a product review.",
    "input_schema": {
        "type": "object",
        "properties": {
            "sentiment": {
                "type": "string",
                "enum": ["positive", "negative", "neutral", "mixed"],
            },
            "confidence":   {"type": "number", "minimum": 0, "maximum": 1},
            "key_phrases":  {"type": "array", "items": {"type": "string"}, "maxItems": 3},
            "would_recommend": {"type": "boolean"},
        },
        "required": ["sentiment", "confidence", "key_phrases", "would_recommend"],
    },
}

MEETING_TOOL = {
    "name": "extract_meeting",
    "description": "Extracts structured meeting details from a calendar invite or email.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title":        {"type": "string"},
            "date":         {"type": "string", "description": "ISO 8601 date, e.g. 2025-06-15"},
            "time":         {"type": "string", "description": "HH:MM in 24h format"},
            "duration_min": {"type": "integer", "description": "Duration in minutes"},
            "attendees":    {"type": "array",  "items": {"type": "string"}},
            "location":     {"type": "string", "description": "Room name or video link"},
        },
        "required": ["title", "date", "attendees"],
    },
}


def structured_extract(text: str, tool: dict) -> dict:
    """Forces Claude to call `tool` and returns the validated input dict."""
    response = client.messages.create(
        model=MODEL_FAST,
        max_tokens=512,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool["name"]},
        messages=[{"role": "user", "content": text}],
    )
    return response.content[0].input   # always a tool_use block


if __name__ == "__main__":
    console.print("\n[bold]Module 5, Lesson 3 — Structured Outputs[/bold]\n")

    # ── Demo 1: Person extraction ─────────────────────────────────────────
    console.print(Rule("Entity extraction"))
    texts = [
        "Hey, I'm Sarah Connor, 29 years old and I live in Los Angeles. Reach me at sarah@example.com.",
        "My colleague Dr. Patel (age 47) recently relocated from Chicago to Seattle.",
    ]
    for text in texts:
        console.print(f"[yellow]Input:[/yellow] {text}")
        result = structured_extract(text, PERSON_TOOL)
        console.print(Panel(json.dumps(result, indent=2), title="Extracted person"))

    # ── Demo 2: Sentiment classification ────────────────────────────────
    console.print(Rule("Sentiment classification"))
    reviews = [
        "This laptop is incredible — fast, lightweight, and the battery lasts all day. Highly recommend!",
        "Terrible experience. The product broke after two days and customer support never responded.",
        "It's okay. Does what it says but nothing special. Wouldn't go out of my way to recommend it.",
    ]
    for review in reviews:
        console.print(f"[yellow]Review:[/yellow] {review[:80]}...")
        result = structured_extract(review, SENTIMENT_TOOL)
        color  = {"positive": "green", "negative": "red", "neutral": "dim", "mixed": "yellow"}.get(
            result["sentiment"], "white"
        )
        console.print(
            f"  Sentiment: [{color}]{result['sentiment']}[/{color}] "
            f"(conf: {result['confidence']:.2f}) | "
            f"Recommend: {result['would_recommend']}"
        )
        console.print(f"  Key phrases: {result['key_phrases']}\n")

    # ── Demo 3: Meeting extraction ────────────────────────────────────────
    console.print(Rule("Meeting extraction"))
    invite = (
        "Hi team, let's meet on June 15th at 14:30 for the Q3 planning session. "
        "The meeting will be 90 minutes in Conference Room B. "
        "Please confirm: Alice, Bob, and Carol."
    )
    console.print(f"[yellow]Invite:[/yellow] {invite}")
    result = structured_extract(invite, MEETING_TOOL)
    console.print(Panel(json.dumps(result, indent=2), title="Extracted meeting"))

    console.print("[bold green]✓ Lesson 3 complete![/bold green]")
    console.print("Next: [italic]python code/module6/lesson1_evaluation.py[/italic]\n")
