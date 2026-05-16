"""
Module 5, Lesson 2: Designing and Integrating Tools
=====================================================
Demonstrates the 5 rules of good tool design through
side-by-side comparisons of well-designed vs poorly-designed
tool definitions.

Run:
    python code/module5/lesson2_tool_design.py
"""

import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table

load_dotenv()
client  = Anthropic()
console = Console()
MODEL   = "claude-haiku-4-5-20251001"


def call_with_tool(user_query: str, tool_def: dict) -> dict | None:
    """Sends a query with a single tool and returns the tool call arguments, or None."""
    response = client.messages.create(
        model=MODEL, max_tokens=256,
        tools=[tool_def],
        messages=[{"role": "user", "content": user_query}]
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return None


# ─────────────────────────────────────────────
#  RULE 1 DEMO: Vague vs precise description
#  The description tells Claude WHEN to call it.
# ─────────────────────────────────────────────
TOOL_VAGUE_DESC = {
    "name": "search",
    "description": "Search for things.",   # Bad: what things? when?
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {"type": "string"}
        },
        "required": ["query"]
    }
}

TOOL_PRECISE_DESC = {
    "name": "search_products",
    "description": (
        "Searches the ACME product catalogue by keyword. "
        "Use this when the user asks about product availability, pricing, or specifications. "
        "Do NOT use for HR or policy questions."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type":        "string",
                "description": "Product keyword, e.g. 'smart fridge', 'air purifier Series B'"
            }
        },
        "required": ["query"]
    }
}


# ─────────────────────────────────────────────
#  RULE 2 DEMO: Missing enum vs enum-constrained
#  Without enum, Claude may pass invalid values.
# ─────────────────────────────────────────────
TOOL_NO_ENUM = {
    "name": "get_report",
    "description": "Retrieves a business report by type.",
    "input_schema": {
        "type": "object",
        "properties": {
            "report_type": {
                "type":        "string",
                "description": "The type of report"  # Claude will guess
            },
            "quarter": {
                "type":        "string",
                "description": "The quarter"         # Claude will guess format
            }
        },
        "required": ["report_type", "quarter"]
    }
}

TOOL_WITH_ENUM = {
    "name": "get_report",
    "description": "Retrieves a business report by type and quarter.",
    "input_schema": {
        "type": "object",
        "properties": {
            "report_type": {
                "type":        "string",
                "enum":        ["revenue", "expenses", "headcount", "churn"],
                "description": "The category of business metric to report on"
            },
            "quarter": {
                "type":        "string",
                "enum":        ["Q1", "Q2", "Q3", "Q4"],
                "description": "The fiscal quarter, e.g. 'Q3'"
            }
        },
        "required": ["report_type", "quarter"]
    }
}


# ─────────────────────────────────────────────
#  RULE 3 DEMO: Over-required vs correct required
#  Over-requiring forces Claude to hallucinate values.
# ─────────────────────────────────────────────
TOOL_OVER_REQUIRED = {
    "name": "book_meeting",
    "description": "Books a calendar meeting.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title":       {"type": "string",  "description": "Meeting title"},
            "date":        {"type": "string",  "description": "Date in YYYY-MM-DD"},
            "time":        {"type": "string",  "description": "Time in HH:MM"},
            "attendees":   {"type": "array",   "items": {"type": "string"}, "description": "Email list"},
            "location":    {"type": "string",  "description": "Room or video link"},
            "description": {"type": "string",  "description": "Meeting agenda"},
        },
        # Bug: location and description are optional but listed as required
        "required": ["title", "date", "time", "attendees", "location", "description"]
    }
}

TOOL_CORRECT_REQUIRED = {
    "name": "book_meeting",
    "description": "Books a calendar meeting. Only title, date, time, and attendees are required.",
    "input_schema": {
        "type": "object",
        "properties": {
            "title":       {"type": "string",  "description": "Meeting title"},
            "date":        {"type": "string",  "description": "Date in YYYY-MM-DD format"},
            "time":        {"type": "string",  "description": "Start time in HH:MM (24h)"},
            "attendees":   {"type": "array",   "items": {"type": "string"}, "description": "Attendee email addresses"},
            "location":    {"type": "string",  "description": "Optional: room name or video link"},
            "description": {"type": "string",  "description": "Optional: meeting agenda or notes"},
        },
        "required": ["title", "date", "time", "attendees"]  # Only truly mandatory fields
    }
}


if __name__ == "__main__":
    console.print("\n[bold]Module 5, Lesson 2: Tool Design Rules[/bold]\n")

    # ── Rule 1: Description quality ───────────
    console.print("[bold cyan]Rule 1: Write descriptions for Claude, not humans[/bold cyan]")
    query = "Do you have any SmartFridge models in stock?"

    args_vague   = call_with_tool(query, TOOL_VAGUE_DESC)
    args_precise = call_with_tool(query, TOOL_PRECISE_DESC)

    console.print(
        Columns([
            Panel(f"Tool called: search\nArgs: {args_vague}",
                  title="[red]Vague description[/red]", width=44),
            Panel(f"Tool called: search_products\nArgs: {args_precise}",
                  title="[green]Precise description[/green]", width=44),
        ])
    )

    # ── Rule 2: Enum constraints ──────────────
    console.print("\n[bold cyan]Rule 2: Use enum for fixed-value parameters[/bold cyan]")
    query2 = "Show me the revenue report for Q3."

    args_no_enum   = call_with_tool(query2, TOOL_NO_ENUM)
    args_with_enum = call_with_tool(query2, TOOL_WITH_ENUM)

    console.print(
        Columns([
            Panel(f"Args: {json.dumps(args_no_enum,   indent=2)}",
                  title="[red]No enum — Claude guesses format[/red]", width=44),
            Panel(f"Args: {json.dumps(args_with_enum, indent=2)}",
                  title="[green]Enum — always valid values[/green]", width=44),
        ])
    )

    # ── Rule 3: Required fields ───────────────
    console.print("\n[bold cyan]Rule 3: Only list truly mandatory params in 'required'[/bold cyan]")
    query3 = "Schedule a team sync with alice@acme.com for tomorrow at 2pm."

    args_over    = call_with_tool(query3, TOOL_OVER_REQUIRED)
    args_correct = call_with_tool(query3, TOOL_CORRECT_REQUIRED)

    console.print("[dim]Over-required — Claude must hallucinate location and description:[/dim]")
    console.print(Panel(json.dumps(args_over,    indent=2), title="[red]Over-required[/red]"))
    console.print("[dim]Correct — only fills in what the user actually specified:[/dim]")
    console.print(Panel(json.dumps(args_correct, indent=2), title="[green]Correct required fields[/green]"))

    console.print("\n[bold green]✓ Lesson 2 complete![/bold green]")
    console.print("Next: [italic]python code/module6/lesson1_evaluation.py[/italic]\n")
