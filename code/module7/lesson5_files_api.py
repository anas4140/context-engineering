"""
Module 7, Lesson 5: Files API
==============================
Demonstrates uploading a text document once and referencing it by ID
across multiple queries — without resending the bytes each time.

Run:
    python code/module7/lesson5_files_api.py
"""

import os
import sys
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
#  Sample document — in production this would
#  be an actual PDF or large text file
# ─────────────────────────────────────────────
SAMPLE_DOCUMENT = b"""
ACME Inc. — Employee Handbook (Excerpt)

PAID TIME OFF
Full-time employees receive 20 days of Paid Time Off (PTO) per year.
PTO accrues at 1.67 days per month starting from the first day of employment.
Up to 10 unused PTO days may be rolled over to the following calendar year.

REMOTE WORK POLICY
Employees may work remotely up to 3 days per week with manager approval.
Remote work is not permitted during the first 90 days of employment.
All remote employees must be available during core hours: 10 AM – 3 PM local time.

PARENTAL LEAVE
Primary caregivers receive 16 weeks of fully paid parental leave.
Secondary caregivers receive 4 weeks of fully paid parental leave.
Leave must be taken within 12 months of the child's birth or adoption date.

EXPENSE REIMBURSEMENT
Submit all business expenses within 30 days of the transaction via Expensify.
Expenses over $500 require pre-approval from your department head.
Travel expenses are reimbursed at the IRS standard mileage rate.
""".strip()

QUESTIONS = [
    "How many PTO days do full-time employees receive per year?",
    "Can I work from home every day of the week?",
    "How long is parental leave for primary caregivers?",
    "What is the deadline for submitting expense reports?",
]


def upload_document(content: bytes, filename: str) -> str:
    """Uploads a document to the Files API and returns its file_id."""
    file_obj = client.beta.files.upload(
        file=(filename, content, "text/plain"),
    )
    return file_obj.id


def query_file(file_id: str, question: str) -> str:
    """Answers a question about an uploaded file using its ID — no bytes resent."""
    response = client.beta.messages.create(
        model=MODEL_FAST,
        max_tokens=256,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {
                        "type":    "file",
                        "file_id": file_id,
                    },
                    "title": "Employee Handbook",
                },
                {"type": "text", "text": question},
            ],
        }],
        betas=["files-api-2025-04-14"],
    )
    return response.content[0].text


if __name__ == "__main__":
    console.print("\n[bold]Module 7, Lesson 5 — Files API[/bold]\n")

    # ── Upload once ──────────────────────────────────────────────────────
    console.print("[dim]Uploading document...[/dim]")
    file_id = upload_document(SAMPLE_DOCUMENT, "employee_handbook.txt")
    console.print(f"[green]Uploaded.[/green] file_id = {file_id}\n")
    console.print("[dim]Document bytes are now stored server-side — not resent per query.[/dim]\n")

    # ── Query multiple times using the same file_id ──────────────────────
    for question in QUESTIONS:
        console.print(Rule())
        console.print(f"[yellow]Q:[/yellow] {question}")
        answer = query_file(file_id, question)
        console.print(Panel(answer, title="[green]Answer[/green]"))

    # ── List and clean up ────────────────────────────────────────────────
    console.print(Rule("File management"))
    files = client.beta.files.list()
    console.print(f"Files currently stored: {len(files.data)}")

    client.beta.files.delete(file_id)
    console.print(f"[dim]Deleted {file_id}[/dim]")

    console.print("\n[bold green]✓ Lesson 5 complete![/bold green]")
    console.print("Next: [italic]python code/module8/lesson1_extended_thinking.py[/italic]\n")
