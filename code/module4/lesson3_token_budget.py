"""
Module 4, Lesson 3: Token Budget Management
============================================
Implements a multi-turn conversation manager that:
  - Tracks token usage every turn
  - Triggers history summarisation at 80% budget
  - Prevents context window overflow gracefully

Run:
    python code/module4/lesson3_token_budget.py
"""

import os
import tiktoken
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule

load_dotenv()
client  = Anthropic()
console = Console()
enc     = tiktoken.get_encoding("cl100k_base")
MODEL   = "claude-haiku-4-5-20251001"

# Budget constants
CONTEXT_LIMIT   = 200_000   # Claude's context window
OUTPUT_RESERVE  = 2_048     # Always keep room for the response
COMPRESS_THRESH = 0.80      # Compress at 80% capacity


def tok(text: str) -> int:
    """Count tokens in a string."""
    return len(enc.encode(text))


def total_tokens(system: str, history: list[dict], extra: str = "") -> int:
    """Estimate total input tokens for a request."""
    t = tok(system) + tok(extra)
    for m in history:
        content = m["content"]
        if isinstance(content, str):
            t += tok(content)
    return t


# ─────────────────────────────────────────────
#  HISTORY COMPRESSION
#  When budget hits 80%, summarise old turns
#  into a compact summary and replace them.
# ─────────────────────────────────────────────
def compress_history(history: list[dict], keep_recent: int = 4) -> list[dict]:
    """
    Compresses old conversation turns into a summary.

    Strategy:
    - Keep the most recent `keep_recent` turns intact (recency effect)
    - Summarise all older turns into a single assistant message
    - Return the summary + recent turns as the new history

    Args:
        history:      full conversation history
        keep_recent:  number of recent turns to keep verbatim

    Returns:
        compressed history (summary message + recent turns)
    """
    if len(history) <= keep_recent:
        return history   # Nothing to compress

    old_turns   = history[:-keep_recent]
    recent_turns = history[-keep_recent:]

    # Format old turns for the summariser
    old_text = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in old_turns
        if isinstance(m["content"], str)
    )

    summary_response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        system="You are a conversation summariser. Be concise and factual.",
        messages=[{
            "role":    "user",
            "content": (
                f"Summarise the key facts and decisions from this conversation "
                f"in 3-5 sentences:\n\n{old_text}"
            )
        }]
    )
    summary_text = summary_response.content[0].text

    # Replace old turns with a single summary block
    summary_message = {
        "role":    "assistant",
        "content": f"[Conversation summary — earlier turns compressed]\n{summary_text}"
    }

    compressed = [summary_message] + recent_turns
    return compressed


# ─────────────────────────────────────────────
#  BUDGET-AWARE CONVERSATION MANAGER
# ─────────────────────────────────────────────
class BudgetAwareConversation:
    """
    Manages a multi-turn conversation with automatic token budget tracking
    and history compression when the budget threshold is reached.
    """

    def __init__(self, system_prompt: str, budget: int = CONTEXT_LIMIT):
        self.system   = system_prompt
        self.budget   = budget
        self.history  = []
        self.turn     = 0

    def _available(self) -> int:
        return self.budget - OUTPUT_RESERVE

    def _used(self, extra: str = "") -> int:
        return total_tokens(self.system, self.history, extra)

    def _pct(self, extra: str = "") -> float:
        return self._used(extra) / self._available()

    def chat(self, user_message: str) -> str:
        """
        Sends a message, compresses history if needed, returns the reply.
        """
        self.turn += 1
        pct_before = self._pct(user_message)

        console.print(
            f"[dim]Turn {self.turn} | Budget: {self._used(user_message):,} / "
            f"{self._available():,} tokens ({pct_before:.1%})[/dim]"
        )

        # Compress if above threshold
        if pct_before > COMPRESS_THRESH:
            console.print(
                f"[yellow]⚠ Budget at {pct_before:.1%} — compressing history...[/yellow]"
            )
            before = len(self.history)
            self.history = compress_history(self.history)
            after = len(self.history)
            console.print(
                f"[green]  Compressed {before} turns → {after} turns "
                f"(new budget: {self._pct(user_message):.1%})[/green]"
            )

        # Add user message and call the API
        self.history.append({"role": "user", "content": user_message})

        response = client.messages.create(
            model=MODEL,
            max_tokens=OUTPUT_RESERVE,
            system=self.system,
            messages=self.history,
        )
        reply = response.content[0].text

        # Add assistant reply to history
        self.history.append({"role": "assistant", "content": reply})
        return reply


if __name__ == "__main__":
    console.print("\n[bold]Module 4, Lesson 3: Token Budget Management[/bold]\n")

    system = (
        "You are a helpful research assistant. "
        "Remember information shared earlier in our conversation. "
        "Be concise in your replies."
    )

    convo = BudgetAwareConversation(system_prompt=system)

    # Simulate a multi-turn conversation that builds up history
    exchanges = [
        "Hi! I'm researching renewable energy. Can you explain solar PV briefly?",
        "How does solar PV compare to wind energy in terms of land use?",
        "What about offshore wind — is it more efficient?",
        "Can you summarise the cost trends for both since 2010?",
        "Which technology has the fastest growing installed capacity right now?",
        "Based on everything we've discussed, what would you recommend for a coastal city?",
    ]

    console.print(Rule("Multi-turn conversation with budget tracking"))

    for user_msg in exchanges:
        console.print(f"\n[bold yellow]User:[/bold yellow] {user_msg}")
        reply = convo.chat(user_msg)
        console.print(f"[bold green]Assistant:[/bold green] {reply[:300]}")

    console.print(f"\n[bold]Final history length:[/bold] {len(convo.history)} messages")
    console.print(f"[bold]Final budget used:[/bold]    {convo._pct():.1%}")
    console.print("\n[bold green]✓ Lesson 3 complete![/bold green]")
    console.print("Next: [italic]python code/module5/lesson_agent_loop.py[/italic]\n")
