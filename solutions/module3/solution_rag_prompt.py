"""
SOLUTION: Module 3, Lesson 1 — Design a RAG Prompt

Hands-on task:
  Write a complete system prompt for the Generator (LLM) given:
  - A retrieved context chunk about PTO policy
  - The user's question about vacation time

Run:
    python solutions/module3/solution_rag_prompt.py
"""

from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()
client  = Anthropic()
console = Console()


# ─────────────────────────────────────────────
#  ANSWER: Complete RAG Generator prompt
# ─────────────────────────────────────────────

# This is the retrieved context the "Retriever" found
RETRIEVED_CONTEXT = """Source: "employee_handbook.pdf", page 12
Title: "Time Off Policy"
Content: "Full-time employees receive 20 days of Paid Time Off (PTO) per year.
PTO accrues at a rate of 1.67 days per month. Unused PTO can be rolled over,
up to a maximum of 10 days. New employees start with a balance of 0 days and
begin accruing PTO on their first day."
"""

USER_QUESTION = "How much vacation time do I get, and can I save it for next year if I don't use it?"


def build_rag_generator_prompt(retrieved_context: str, user_question: str) -> tuple[str, str]:
    """
    Returns the (system_prompt, user_message) pair for the RAG generator.

    A good RAG system prompt has 3 parts:
    1. Persona   — who the model is and what it does
    2. Rules     — what it MUST and MUST NOT do
    3. Structure — how to format the output
    """

    # ── System prompt ────────────────────────
    system_prompt = """You are a helpful HR assistant for ACME Inc.

Your job is to answer employee questions about company policies ACCURATELY and CONCISELY.

RULES YOU MUST FOLLOW:
1. Answer ONLY using information from the <context> provided below.
2. If the answer to the question is NOT found in the context, respond with:
   "I don't have that information in the provided policy documents. Please contact HR directly."
3. ALWAYS cite your source. Format: (Source: <filename>, page <number>)
4. Do NOT add information from your own knowledge — only use the provided context.
5. If the context is ambiguous, say so and suggest the employee confirm with HR."""

    # ── User message (context + question) ────
    # We inject the retrieved context + question into the user turn.
    # Using XML tags to clearly separate context from question.
    user_message = f"""<context>
{retrieved_context}
</context>

Employee question: {user_question}"""

    return system_prompt, user_message


def run_rag_demo(context: str, question: str) -> str:
    system_prompt, user_message = build_rag_generator_prompt(context, question)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )
    return response.content[0].text


if __name__ == "__main__":
    console.print("\n[bold]Solution: Module 3, Lesson 1 — RAG Generator Prompt[/bold]\n")

    # ── Show the assembled prompt ─────────────
    system_prompt, user_message = build_rag_generator_prompt(
        RETRIEVED_CONTEXT, USER_QUESTION
    )

    console.print("[bold cyan]System prompt (Generator instructions):[/bold cyan]")
    console.print(Panel(system_prompt))

    console.print("[bold cyan]User message (context + question):[/bold cyan]")
    console.print(Panel(user_message))

    # ── Run it and show the answer ────────────
    console.print("[bold cyan]Model output:[/bold cyan]")
    answer = run_rag_demo(RETRIEVED_CONTEXT, USER_QUESTION)
    console.print(Panel(answer, title="HR Assistant Response"))

    # ── Test the "not found" fallback ─────────
    console.print("\n[bold cyan]Test: question NOT in the context[/bold cyan]")
    out_of_scope = run_rag_demo(
        RETRIEVED_CONTEXT,
        "What is the company's parental leave policy?"
    )
    console.print(Panel(out_of_scope, title="Out-of-scope question response"))

    console.print("\n[bold green]✓ Solution complete![/bold green]\n")
