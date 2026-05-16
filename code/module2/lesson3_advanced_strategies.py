"""
Module 2, Lesson 3: Advanced Prompt Strategies
================================================
Demonstrates: prompt chaining, self-consistency sampling, and meta-prompting.

Run:
    python code/module2/lesson3_advanced_strategies.py
"""

import os
from collections import Counter
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

load_dotenv()
client  = Anthropic()
console = Console()
MODEL   = "claude-haiku-4-5-20251001"


def call(system: str, user: str, max_tokens: int = 512) -> str:
    r = client.messages.create(
        model=MODEL, max_tokens=max_tokens, system=system,
        messages=[{"role": "user", "content": user}]
    )
    return r.content[0].text.strip()


# ─────────────────────────────────────────────
#  TECHNIQUE 1: PROMPT CHAINING
#  Break a complex task into focused steps.
#  Each step's output feeds the next.
# ─────────────────────────────────────────────
def chain_research_summary(raw_text: str) -> dict:
    """
    3-step chain:
      Step 1 — Extract all factual claims
      Step 2 — Flag any uncertain or hedged claims
      Step 3 — Write a polished summary using only confident claims
    """

    # Step 1: Extract claims
    claims = call(
        system="You are a precise fact extractor. Extract every factual claim as a bullet list. No commentary.",
        user=f"Extract all factual claims from:\n\n{raw_text}"
    )
    console.print(Panel(claims, title="[cyan]Step 1: Extracted claims[/cyan]"))

    # Step 2: Flag uncertain claims
    flagged = call(
        system="You are a fact-checker. Mark each claim as CONFIDENT or UNCERTAIN. Keep the bullet format.",
        user=f"Classify each claim as CONFIDENT or UNCERTAIN:\n\n{claims}"
    )
    console.print(Panel(flagged, title="[cyan]Step 2: Confidence flagging[/cyan]"))

    # Step 3: Write final summary using only confident claims
    summary = call(
        system=(
            "You are a technical writer. Write a concise 2-3 sentence summary "
            "using ONLY the CONFIDENT claims. Ignore all UNCERTAIN ones."
        ),
        user=f"Write a summary from these assessed claims:\n\n{flagged}"
    )
    console.print(Panel(summary, title="[cyan]Step 3: Final summary[/cyan]"))

    return {"claims": claims, "flagged": flagged, "summary": summary}


# ─────────────────────────────────────────────
#  TECHNIQUE 2: SELF-CONSISTENCY SAMPLING
#  Run the same prompt N times and take the
#  majority answer. Reduces variance on
#  reasoning and maths tasks.
# ─────────────────────────────────────────────
def self_consistency(problem: str, n_samples: int = 5) -> str:
    """
    Samples the model n_samples times and returns the majority answer.
    Each call uses temperature=1 (default) for diversity.
    """
    system = (
        "Solve the problem step by step. "
        "End your response with 'FINAL ANSWER: <number or value>' on its own line."
    )

    answers = []
    for i in range(n_samples):
        response = call(system, problem)
        # Extract the final answer line
        for line in reversed(response.split("\n")):
            if "FINAL ANSWER:" in line:
                answer = line.replace("FINAL ANSWER:", "").strip()
                answers.append(answer)
                break
        else:
            answers.append("PARSE_ERROR")

    # Count votes
    vote_counts = Counter(answers)
    majority    = vote_counts.most_common(1)[0][0]
    votes_str   = ", ".join(f"{ans}: {cnt}x" for ans, cnt in vote_counts.items())

    console.print(f"  All answers: {votes_str}")
    console.print(f"  Majority:    [green]{majority}[/green]")
    return majority


# ─────────────────────────────────────────────
#  TECHNIQUE 3: META-PROMPTING
#  Use Claude to improve your own prompts.
# ─────────────────────────────────────────────
def meta_improve_prompt(original_prompt: str, failure_description: str) -> str:
    """
    Asks Claude to rewrite a prompt to fix a described failure mode.
    """
    meta_system = (
        "You are an expert prompt engineer. "
        "Your job is to improve prompts to fix specific failure modes. "
        "Return ONLY the improved prompt text — no explanation, no preamble."
    )
    meta_user = (
        f"Original prompt:\n{original_prompt}\n\n"
        f"Failure mode to fix: {failure_description}\n\n"
        "Write an improved version of the prompt:"
    )
    return call(meta_system, meta_user)


if __name__ == "__main__":
    console.print("\n[bold]Module 2, Lesson 3: Advanced Prompt Strategies[/bold]\n")

    # ── Technique 1: Prompt chaining ──────────
    console.print(Rule("Technique 1: Prompt Chaining"))
    sample_text = (
        "Our new battery technology achieves 500 Wh/kg energy density, "
        "which may represent a significant improvement over current lithium-ion cells. "
        "The technology reportedly charges to 80% in under 10 minutes. "
        "Some experts suggest it could reach mass production by 2027, "
        "though manufacturing challenges remain unresolved. "
        "The company claims it is 40% cheaper to produce than existing solutions."
    )
    chain_research_summary(sample_text)

    # ── Technique 2: Self-consistency ─────────
    console.print(Rule("\nTechnique 2: Self-Consistency Sampling (n=5)"))
    problem = (
        "A train leaves City A at 8:00 AM travelling at 90 km/h. "
        "Another train leaves City B (450 km away) at 9:00 AM travelling at 110 km/h toward City A. "
        "At what time do they meet?"
    )
    console.print(f"Problem: [yellow]{problem}[/yellow]")
    majority_answer = self_consistency(problem, n_samples=5)

    # ── Technique 3: Meta-prompting ───────────
    console.print(Rule("\nTechnique 3: Meta-Prompting"))
    weak_prompt = "Summarise the document."
    failure     = "Output length and format are inconsistent — sometimes 1 sentence, sometimes 5 paragraphs."

    console.print(f"Original:    [red]{weak_prompt}[/red]")
    console.print(f"Failure:     [dim]{failure}[/dim]")
    improved = meta_improve_prompt(weak_prompt, failure)
    console.print(Panel(improved, title="[green]Improved prompt[/green]"))

    console.print("\n[bold green]✓ Module 2 complete![/bold green]")
    console.print("Next: [italic]python code/module3/lesson1_rag_pipeline.py[/italic]\n")
