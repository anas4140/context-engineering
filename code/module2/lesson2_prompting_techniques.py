"""
Module 2, Lesson 2 & 3: Prompting Techniques
=============================================
Demonstrates: Zero-shot, Few-shot, Chain-of-Thought, and ReAct prompting.
Each function is a self-contained, runnable example.

Run:
    python code/module2/lesson2_prompting_techniques.py
"""

import os
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()
client = Anthropic()
console = Console()

MODEL = "claude-haiku-4-5-20251001"


# ─────────────────────────────────────────────
#  1. ZERO-SHOT PROMPTING
#  Give the model a task with NO examples.
#  Works well for simple, common tasks.
# ─────────────────────────────────────────────
def zero_shot(task: str) -> str:
    """
    Sends the task directly with no examples or special instructions.
    The model relies entirely on its training data.
    """
    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": task}]
    )
    return response.content[0].text


# ─────────────────────────────────────────────
#  2. FEW-SHOT PROMPTING
#  Provide 2–3 input/output examples BEFORE
#  the actual task. This "shows" the model the
#  exact format and style you want.
# ─────────────────────────────────────────────
def few_shot_sentiment(review: str) -> str:
    """
    Classifies a product review as POSITIVE, NEGATIVE, or NEUTRAL.
    Uses 3 examples to teach the model the exact output format.
    """
    # Each example is a user message + assistant reply pair.
    # This is called the "few-shot" or "in-context learning" setup.
    few_shot_messages = [
        # Example 1 — positive
        {"role": "user",      "content": "Review: The battery lasts all day and the screen is gorgeous.\nSentiment:"},
        {"role": "assistant", "content": "POSITIVE"},

        # Example 2 — negative
        {"role": "user",      "content": "Review: It broke after two weeks and customer support was useless.\nSentiment:"},
        {"role": "assistant", "content": "NEGATIVE"},

        # Example 3 — neutral
        {"role": "user",      "content": "Review: It does what it says. Nothing special, nothing bad.\nSentiment:"},
        {"role": "assistant", "content": "NEUTRAL"},

        # The ACTUAL task — same format as the examples above
        {"role": "user",      "content": f"Review: {review}\nSentiment:"},
    ]

    response = client.messages.create(
        model=MODEL,
        max_tokens=10,   # We only need one word back
        messages=few_shot_messages
    )
    return response.content[0].text.strip()


# ─────────────────────────────────────────────
#  3. CHAIN-OF-THOUGHT (CoT) PROMPTING
#  Ask the model to "think step by step" before
#  giving its final answer. Dramatically improves
#  accuracy on reasoning and maths tasks.
# ─────────────────────────────────────────────
def chain_of_thought(problem: str) -> str:
    """
    Solves a word problem using explicit step-by-step reasoning.
    Adding "think step by step" can improve accuracy by 20-40% on hard problems.
    """
    # The magic phrase: "think step by step" triggers CoT behaviour
    cot_prompt = (
        f"{problem}\n\n"
        "Think through this step by step before giving your final answer. "
        "Show your reasoning clearly."
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        messages=[{"role": "user", "content": cot_prompt}]
    )
    return response.content[0].text


# ─────────────────────────────────────────────
#  4. XML-STRUCTURED PROMPTING
#  Use XML tags to clearly separate different
#  types of content in a single prompt.
#  Reduces ambiguity and improves reliability.
# ─────────────────────────────────────────────
def xml_structured_analysis(document: str, question: str) -> str:
    """
    Uses XML tags to cleanly separate the document from the question.
    This is especially important for preventing prompt injection (Module 6).
    """
    # Wrapping user-provided content in tags tells the model
    # "this is DATA, not INSTRUCTIONS"
    structured_prompt = f"""You are a precise document analyst.
Answer the question using ONLY the information inside the <document> tags.
If the answer is not in the document, say "Not found in document."

<document>
{document}
</document>

<question>
{question}
</question>

Provide a concise answer:"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": structured_prompt}]
    )
    return response.content[0].text


# ─────────────────────────────────────────────
#  5. ROLE PROMPTING
#  Assign the model a specific expert persona.
#  Often improves quality for specialised domains.
# ─────────────────────────────────────────────
def role_prompting(question: str, role: str) -> str:
    """
    Assigns a domain expert persona to the model via the system prompt.
    Compare responses with and without a role.
    """
    system = (
        f"You are an expert {role} with 20 years of experience. "
        "Give precise, practical advice. Use domain-specific terminology "
        "where appropriate but explain any jargon."
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        system=system,
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text


if __name__ == "__main__":
    console.print("\n[bold]Module 2: Prompting Techniques Demo[/bold]\n")

    # ── 1. Zero-shot ─────────────────────────
    console.print("[bold cyan]1. Zero-shot prompting[/bold cyan]")
    result = zero_shot("Translate 'Hello, how are you?' into French.")
    console.print(Panel(result, title="Zero-shot result"))

    # ── 2. Few-shot ──────────────────────────
    console.print("\n[bold cyan]2. Few-shot sentiment classification[/bold cyan]")
    reviews = [
        "Absolutely love it, best purchase I've made this year!",
        "Terrible quality, fell apart on day one.",
        "It arrived on time and works as described.",
    ]
    for review in reviews:
        sentiment = few_shot_sentiment(review)
        console.print(f"  [{sentiment}] {review[:60]}...")

    # ── 3. Chain-of-thought ──────────────────
    console.print("\n[bold cyan]3. Chain-of-thought reasoning[/bold cyan]")
    problem = (
        "A store sells apples for $0.50 each and oranges for $0.75 each. "
        "If you buy 3 apples and 4 oranges, and pay with a $5 bill, "
        "how much change do you get?"
    )
    result = chain_of_thought(problem)
    console.print(Panel(result, title="CoT result"))

    # ── 4. XML structured ────────────────────
    console.print("\n[bold cyan]4. XML-structured prompting[/bold cyan]")
    doc = (
        "ACME Warranty Policy: All products carry a 2-year limited warranty. "
        "The warranty covers manufacturing defects but not accidental damage. "
        "To make a claim, contact support@acme.com with your order number."
    )
    answer = xml_structured_analysis(doc, "How long is the warranty?")
    console.print(Panel(answer, title="XML-structured result"))

    # ── 5. Role prompting ────────────────────
    console.print("\n[bold cyan]5. Role prompting[/bold cyan]")
    question = "What is the most important thing to consider when designing a database schema?"
    result = role_prompting(question, "database architect")
    console.print(Panel(result[:400] + "...", title="Role prompting result"))

    console.print("\n[bold green]✓ Module 2 complete![/bold green]")
    console.print("Next: [italic]python code/module3/lesson1_rag_pipeline.py[/italic]\n")
