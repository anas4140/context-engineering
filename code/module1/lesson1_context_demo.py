"""
Module 1, Lesson 1: What is Context and Why is it Critical?
============================================================
This script demonstrates the difference between POOR context and RICH context
when calling an LLM. Run it and compare the two responses side by side.

Run:
    python code/module1/lesson1_context_demo.py
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns

# Load ANTHROPIC_API_KEY from your .env file
load_dotenv()

# Create the Anthropic client (reads key from environment automatically)
client = Anthropic()
console = Console()


# ─────────────────────────────────────────────
#  SCENARIO A: Poor Context
#  The AI only gets the raw user question.
#  No system prompt, no history, no knowledge.
# ─────────────────────────────────────────────
def call_with_poor_context(user_question: str) -> str:
    """
    Sends ONLY the user's question to the model.
    No system instructions, no chat history, no retrieved knowledge.
    """
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",   # fast, cheap — good for demos
        max_tokens=256,
        messages=[
            {"role": "user", "content": user_question}
        ]
    )
    # The response content is a list of blocks; [0].text gets the text
    return response.content[0].text


# ─────────────────────────────────────────────
#  SCENARIO B: Rich Context
#  The AI gets a system prompt (its "job description"),
#  chat history (short-term memory), and a retrieved
#  knowledge snippet (from a product manual).
# ─────────────────────────────────────────────
def call_with_rich_context(user_question: str) -> str:
    """
    Sends the user's question PLUS:
    - A detailed system prompt (persona + rules)
    - Chat history (so the AI knows which product we're discussing)
    - A retrieved knowledge snippet (the relevant manual section)
    """

    # 1. SYSTEM PROMPT — the AI's "job description"
    #    This tells the model WHO it is, WHAT it should do,
    #    and HOW it should behave.
    system_prompt = (
        "You are a friendly and efficient support assistant for ACME Inc. "
        "products. Use ONLY the information in the conversation and the "
        "retrieved knowledge below to help the user. "
        "If the retrieved knowledge contains the answer, give a specific, "
        "step-by-step solution. Be concise and friendly."
    )

    # 2. CHAT HISTORY — previous turns of the conversation
    #    Without this the AI doesn't know the user has a SmartFridge Series A.
    chat_history = [
        {
            "role": "user",
            "content": "Hi, I need help with my new fridge."
        },
        {
            "role": "assistant",
            "content": "Of course! I can help with that. Can you tell me the model number?"
        },
        {
            "role": "user",
            "content": "It's the ACME SmartFridge Series A."
        },
        {
            "role": "assistant",
            "content": (
                "Thank you! I have the manual for the Series A pulled up. "
                "What seems to be the issue?"
            )
        },
    ]

    # 3. RETRIEVED KNOWLEDGE — a snippet fetched from the product manual
    #    In a real system this would come from a RAG pipeline (Module 3).
    #    For now we hard-code the most relevant manual section.
    retrieved_knowledge = (
        "[Retrieved from: manual_series_a.pdf, page 12]\n"
        "Common Issue: Ice maker not dispensing ice.\n"
        "Cause: The 'Child Lock' feature disables the ice and water dispenser.\n"
        "Solution: Press and hold the 'Lock' button for 3 seconds to deactivate "
        "the Child Lock. A green light will confirm it is unlocked."
    )

    # 4. FINAL USER MESSAGE — combines the user's question AND the knowledge
    #    We inject the retrieved snippet here so the AI can use it.
    final_user_message = (
        f"Retrieved knowledge:\n{retrieved_knowledge}\n\n"
        f"User question: {user_question}"
    )

    # Build the full message list: history + final question
    messages = chat_history + [
        {"role": "user", "content": final_user_message}
    ]

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=256,
        system=system_prompt,
        messages=messages
    )
    return response.content[0].text


# ─────────────────────────────────────────────
#  DEMO: Bias mitigation with system prompts
#  Shows how the system prompt acts as a
#  control mechanism for model behaviour.
# ─────────────────────────────────────────────
def demo_bias_mitigation(job_title: str) -> tuple[str, str]:
    """
    Calls the model twice with the same task but different system prompts.
    Returns (biased_output, unbiased_output) for comparison.
    """

    task = f"Write a two-sentence job description for a {job_title}."

    # Minimal system prompt — no bias guidance
    biased_response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=128,
        system="You are a hiring assistant.",
        messages=[{"role": "user", "content": task}]
    )

    # Engineered system prompt — explicit inclusivity rules
    inclusive_system_prompt = (
        "You are a hiring assistant for a global tech company committed to "
        "diversity and inclusion. Follow these rules strictly:\n"
        "1. Use gender-neutral language (e.g. 'they', 'the candidate').\n"
        "2. Avoid jargon or exclusionary phrases (e.g. 'rockstar', 'ninja').\n"
        "3. Focus on concrete skills and responsibilities.\n"
        "4. Emphasise collaboration and a supportive work environment."
    )

    unbiased_response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=128,
        system=inclusive_system_prompt,
        messages=[{"role": "user", "content": task}]
    )

    return (
        biased_response.content[0].text,
        unbiased_response.content[0].text
    )


# ─────────────────────────────────────────────
#  MAIN — run all demos and print results
# ─────────────────────────────────────────────
if __name__ == "__main__":
    USER_QUESTION = "It's not working, what do I do?"

    console.print("\n[bold]Module 1, Lesson 1: Context Quality Demo[/bold]\n")

    # ── Demo 1: Poor vs Rich Context ──────────
    console.print("[bold cyan]Demo 1: Poor context vs Rich context[/bold cyan]")
    console.print(f"User question: [italic]{USER_QUESTION}[/italic]\n")

    poor  = call_with_poor_context(USER_QUESTION)
    rich_ = call_with_rich_context(USER_QUESTION)

    console.print(
        Columns([
            Panel(poor,  title="[red]Poor context[/red]",  width=50),
            Panel(rich_, title="[green]Rich context[/green]", width=50),
        ])
    )

    # ── Demo 2: Bias mitigation ───────────────
    console.print("\n[bold cyan]Demo 2: Bias mitigation via system prompt[/bold cyan]")
    biased, unbiased = demo_bias_mitigation("software engineer")

    console.print(
        Columns([
            Panel(biased,   title="[red]Minimal system prompt[/red]",     width=50),
            Panel(unbiased, title="[green]Engineered system prompt[/green]", width=50),
        ])
    )

    console.print("\n[bold green]✓ Lesson 1 complete![/bold green]")
    console.print("Next: [italic]python code/module1/lesson2_economics.py[/italic]\n")
