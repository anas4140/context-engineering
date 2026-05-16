"""
SOLUTION: Module 7 — Files API Multi-Document QA
=================================================
Answer key for the Module 7 Lesson 5 task:
Upload two policy documents once, then answer questions that span both
documents using the Files API — without resending bytes per query.

Run:
    python solutions/module7/solution_files_api.py
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

HR_POLICY = b"""
ACME HR POLICY (v3.1)

PTO: Full-time employees receive 20 days PTO/year. Accrual starts day 1.
Up to 10 unused days roll over annually.

PARENTAL LEAVE: Primary caregiver: 16 weeks paid. Secondary: 4 weeks paid.
Must be taken within 12 months of birth/adoption.

REMOTE WORK: Up to 3 days/week with manager approval after 90-day onboarding.
Core hours: 10 AM – 3 PM local time.

EXPENSES: Submit via Expensify within 30 days. Pre-approval required for >$500.
""".strip()

IT_POLICY = b"""
ACME IT SECURITY POLICY (v2.4)

PASSWORDS: Minimum 12 characters, changed every 90 days, no reuse of last 5.
MFA required for all cloud services and VPN access.

DATA CLASSIFICATION: Confidential data must be encrypted at rest (AES-256)
and in transit (TLS 1.2+). Never stored on personal devices.

DEVICE MANAGEMENT: All company laptops must have MDM installed within 24h of
provisioning. Lost/stolen devices must be reported within 1 hour.

INCIDENT RESPONSE: Security incidents reported to security@acme.com immediately.
P0 incidents require on-call escalation within 15 minutes.
""".strip()

CROSS_DOC_QUESTIONS = [
    "Can I work from home before completing onboarding, and must I use MFA on my remote connection?",
    "What are my obligations if I lose my laptop while on parental leave?",
    "How long do I have to submit expenses, and how quickly must I report a security incident?",
]


def upload(content: bytes, filename: str) -> str:
    f = client.beta.files.upload(file=(filename, content, "text/plain"))
    return f.id


def ask_both(file_id_1: str, file_id_2: str, question: str) -> str:
    response = client.beta.messages.create(
        model=MODEL_FAST,
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {"type": "document", "source": {"type": "file", "file_id": file_id_1}, "title": "HR Policy"},
                {"type": "document", "source": {"type": "file", "file_id": file_id_2}, "title": "IT Security Policy"},
                {"type": "text", "text": question},
            ],
        }],
        betas=["files-api-2025-04-14"],
    )
    return response.content[0].text


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 7 — Files API Multi-Document QA[/bold]\n")

    console.print("[dim]Uploading HR policy...[/dim]")
    hr_id = upload(HR_POLICY, "hr_policy.txt")
    console.print(f"  HR policy:  {hr_id}")

    console.print("[dim]Uploading IT security policy...[/dim]")
    it_id = upload(IT_POLICY, "it_policy.txt")
    console.print(f"  IT policy:  {it_id}")

    console.print("\n[dim]Both files uploaded once. Bytes not resent per query.[/dim]\n")

    for question in CROSS_DOC_QUESTIONS:
        console.print(Rule())
        console.print(f"[yellow]Q:[/yellow] {question}")
        answer = ask_both(hr_id, it_id, question)
        console.print(Panel(answer, title="[green]Answer (cross-document)[/green]"))

    # ── Clean up ─────────────────────────────────────────────────────────
    client.beta.files.delete(hr_id)
    client.beta.files.delete(it_id)
    console.print(f"\n[dim]Cleaned up uploaded files.[/dim]")
    console.print("\n[bold green]✓ Solution complete![/bold green]\n")
    console.print(
        "Key insight: two file_ids, one request — cross-document reasoning with "
        "zero bytes resent after the initial upload.\n"
    )
