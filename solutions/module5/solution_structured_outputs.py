"""
SOLUTION: Module 5 — Structured Outputs Pipeline
=================================================
Answer key for the Module 5 Lesson 4 task:
Build a document processing pipeline that extracts structured data from
three document types using forced tool calls — zero string parsing.

Run:
    python solutions/module5/solution_structured_outputs.py
"""

import os
import sys
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from config import MODEL_FAST

load_dotenv()
client  = Anthropic()
console = Console()

# ─────────────────────────────────────────────
#  Tool schemas
# ─────────────────────────────────────────────
INVOICE_TOOL = {
    "name": "extract_invoice",
    "description": "Extracts structured invoice data from text.",
    "input_schema": {
        "type": "object",
        "properties": {
            "invoice_number": {"type": "string"},
            "vendor":         {"type": "string"},
            "amount_usd":     {"type": "number"},
            "due_date":       {"type": "string", "description": "ISO 8601 date"},
            "line_items":     {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "description": {"type": "string"},
                        "amount_usd":  {"type": "number"},
                    },
                    "required": ["description", "amount_usd"],
                },
            },
        },
        "required": ["invoice_number", "vendor", "amount_usd", "due_date"],
    },
}

SUPPORT_TICKET_TOOL = {
    "name": "classify_ticket",
    "description": "Classifies a customer support ticket.",
    "input_schema": {
        "type": "object",
        "properties": {
            "category":  {"type": "string", "enum": ["billing", "technical", "account", "shipping", "other"]},
            "priority":  {"type": "string", "enum": ["low", "medium", "high", "urgent"]},
            "sentiment": {"type": "string", "enum": ["positive", "neutral", "frustrated", "angry"]},
            "summary":   {"type": "string", "maxLength": 120},
            "needs_human_escalation": {"type": "boolean"},
        },
        "required": ["category", "priority", "sentiment", "summary", "needs_human_escalation"],
    },
}

RESUME_TOOL = {
    "name": "extract_resume",
    "description": "Extracts structured candidate data from a resume.",
    "input_schema": {
        "type": "object",
        "properties": {
            "name":         {"type": "string"},
            "email":        {"type": "string"},
            "years_exp":    {"type": "integer"},
            "skills":       {"type": "array", "items": {"type": "string"}, "maxItems": 8},
            "current_role": {"type": "string"},
            "education":    {"type": "string"},
        },
        "required": ["name", "years_exp", "skills"],
    },
}

SAMPLES = [
    {
        "tool": INVOICE_TOOL,
        "label": "Invoice",
        "text": (
            "INVOICE #INV-2025-0892\nFrom: CloudHost Solutions\n"
            "Due: 2025-07-01\n\nServices:\n"
            "  - Compute (10 VMs × $45/mo): $450.00\n"
            "  - Storage (2 TB × $20): $40.00\n"
            "  - Support package: $110.00\nTotal: $600.00"
        ),
    },
    {
        "tool": SUPPORT_TICKET_TOOL,
        "label": "Support ticket",
        "text": (
            "I have been charged TWICE for my subscription this month!!! "
            "Transaction IDs: TXN-88821 and TXN-88830. I demand an immediate refund "
            "or I will dispute the charges with my bank. This is completely unacceptable."
        ),
    },
    {
        "tool": RESUME_TOOL,
        "label": "Resume",
        "text": (
            "Jane Rodriguez | jane@example.com\n"
            "Senior ML Engineer at DataFlow Inc (2019-present) — 7 years total experience.\n"
            "Skills: Python, PyTorch, TensorFlow, Kubernetes, AWS, Spark, SQL, MLflow\n"
            "Education: MSc Computer Science, Stanford University, 2017"
        ),
    },
]


def extract(text: str, tool: dict) -> dict:
    response = client.messages.create(
        model=MODEL_FAST,
        max_tokens=512,
        tools=[tool],
        tool_choice={"type": "tool", "name": tool["name"]},
        messages=[{"role": "user", "content": text}],
    )
    return response.content[0].input


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 5 — Structured Outputs Pipeline[/bold]\n")

    for sample in SAMPLES:
        console.print(f"\n[bold cyan]{sample['label']}[/bold cyan]")
        console.print(f"[dim]Input:[/dim] {sample['text'][:120]}...")

        result = extract(sample["text"], sample["tool"])
        console.print(Panel(json.dumps(result, indent=2), title=f"[green]{sample['label']} (structured)[/green]"))

    console.print("\n[bold]Summary:[/bold]")
    table = Table(show_lines=True)
    table.add_column("Document type")
    table.add_column("Tool used")
    table.add_column("Output always valid JSON?")
    table.add_column("String parsing needed?")
    for s in SAMPLES:
        table.add_row(s["label"], s["tool"]["name"], "[green]Yes[/green]", "[green]No[/green]")
    console.print(table)

    console.print("\n[bold green]✓ Solution complete![/bold green]\n")
    console.print(
        "Key insight: tool_choice forces a tool_use block — the result is always "
        "valid JSON matching your schema, with no parsing logic needed.\n"
    )
