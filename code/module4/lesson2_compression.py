"""
Module 4: Context Window Optimisation
=======================================
Demonstrates three techniques for fitting more useful information
into the context window:
  1. Chunking strategies (fixed-size vs sentence-aware)
  2. Contextual compression (summarise before storing)
  3. Re-ranking retrieved results by relevance score

Run:
    python code/module4/lesson2_compression.py
"""

import os
import re
import tiktoken
from anthropic import Anthropic
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv()
client  = Anthropic()
console = Console()

MODEL = "claude-haiku-4-5-20251001"

# Use tiktoken to count tokens (close approximation for Claude)
enc = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    """Returns the number of tokens in a string."""
    return len(enc.encode(text))


# ─────────────────────────────────────────────
#  TECHNIQUE 1: Chunking strategies
#  Breaking documents into smaller pieces is
#  the first step in any RAG pipeline.
#  The chunk size affects both retrieval quality
#  and how many tokens you use per query.
# ─────────────────────────────────────────────
def chunk_fixed_size(text: str, chunk_size: int = 200, overlap: int = 20) -> list[str]:
    """
    Splits text into chunks of exactly `chunk_size` tokens.
    `overlap` tokens are repeated between consecutive chunks to avoid
    losing context at chunk boundaries.

    Args:
        text:       the document text to split
        chunk_size: target tokens per chunk
        overlap:    tokens to repeat between chunks

    Returns:
        list of text chunks
    """
    tokens = enc.encode(text)
    chunks = []
    start  = 0

    while start < len(tokens):
        end = min(start + chunk_size, len(tokens))
        # Decode back to text
        chunk = enc.decode(tokens[start:end])
        chunks.append(chunk)
        # Move forward by (chunk_size - overlap) so chunks overlap
        start += chunk_size - overlap

    return chunks


def chunk_by_sentence(text: str, max_tokens: int = 200) -> list[str]:
    """
    Splits text at sentence boundaries and groups sentences together
    until the max_tokens limit is reached.
    This produces more semantically coherent chunks than fixed-size splitting.

    Args:
        text:       the document text to split
        max_tokens: maximum tokens per chunk

    Returns:
        list of text chunks
    """
    # Split on sentence-ending punctuation
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    chunks        = []
    current_chunk = []
    current_count = 0

    for sentence in sentences:
        sentence_tokens = count_tokens(sentence)

        # If adding this sentence would exceed the limit, save current chunk
        if current_count + sentence_tokens > max_tokens and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_count = 0

        current_chunk.append(sentence)
        current_count += sentence_tokens

    # Don't forget the last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# ─────────────────────────────────────────────
#  TECHNIQUE 2: Contextual compression
#  Before storing a chunk, summarise it so it
#  takes fewer tokens in the context window
#  while retaining the key information.
# ─────────────────────────────────────────────
def compress_chunk(chunk: str, query: str) -> str:
    """
    Uses Claude to distil a document chunk into only the information
    relevant to the user's query.

    This is called "contextual compression" — you pass the query AND the
    chunk, and ask the model to extract only what matters.

    Args:
        chunk: a document chunk (raw text)
        query: the user's question

    Returns:
        a compressed version of the chunk (fewer tokens, same key info)
    """
    prompt = (
        f"Here is a document chunk:\n\n{chunk}\n\n"
        f"The user's question is: {query}\n\n"
        "Extract and return ONLY the sentences from the chunk that are "
        "directly relevant to answering the question. "
        "If nothing is relevant, return the string 'NOT RELEVANT'. "
        "Do not add any commentary or explanation."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text.strip()


# ─────────────────────────────────────────────
#  TECHNIQUE 3: Re-ranking
#  After retrieval, score each chunk for
#  relevance to the query and re-order them.
#  This ensures the most relevant chunks appear
#  first (important when context window is limited).
# ─────────────────────────────────────────────
def rerank_chunks(query: str, chunks: list[str]) -> list[tuple[float, str]]:
    """
    Asks Claude to score each chunk's relevance to the query on a 0-10 scale,
    then returns the chunks sorted by score (highest first).

    Args:
        query:  the user's question
        chunks: list of retrieved text chunks

    Returns:
        list of (score, chunk) tuples, sorted by score descending
    """
    scored_chunks = []

    for chunk in chunks:
        scoring_prompt = (
            f"On a scale of 0 to 10, how relevant is this text chunk to the "
            f"following question?\n\n"
            f"Question: {query}\n\n"
            f"Chunk: {chunk}\n\n"
            f"Reply with ONLY a single integer between 0 and 10. Nothing else."
        )

        response = client.messages.create(
            model=MODEL,
            max_tokens=5,
            messages=[{"role": "user", "content": scoring_prompt}]
        )

        # Safely parse the score (default to 0 if parsing fails)
        try:
            score = float(response.content[0].text.strip())
        except ValueError:
            score = 0.0

        scored_chunks.append((score, chunk))

    # Sort by score descending — best chunks first
    return sorted(scored_chunks, key=lambda x: x[0], reverse=True)


if __name__ == "__main__":
    console.print("\n[bold]Module 4: Context Window Optimisation[/bold]\n")

    # Sample long document for demos
    long_document = (
        "ACME Inc. Employee Handbook — Section 3: Benefits and Compensation. "
        "Our comprehensive benefits package is designed to support the health, "
        "wellbeing, and financial security of our employees and their families. "
        "Health Insurance: All full-time employees are eligible from day one. "
        "The company covers 80% of the monthly premium. "
        "Dental coverage includes two cleanings per year at no cost. "
        "Vision benefits cover one eye exam and up to $200 toward frames annually. "
        "Retirement: ACME matches 401(k) contributions up to 4% of base salary. "
        "Vesting is immediate for company match contributions. "
        "Employees may contribute up to the IRS annual limit. "
        "Paid Time Off: Full-time employees receive 20 PTO days per year. "
        "PTO accrues monthly and up to 10 days may be rolled over. "
        "Sick leave is separate: 10 days per year, no rollover. "
        "Parental Leave: Primary caregivers receive 16 weeks of paid leave. "
        "Secondary caregivers receive 4 weeks. "
        "Leave must be taken within 12 months of the child's birth or adoption."
    )

    query = "How many PTO days do I get and can I roll them over?"

    # ── Technique 1: Chunking comparison ─────
    console.print("[bold cyan]Technique 1: Chunking strategies[/bold cyan]")

    fixed_chunks    = chunk_fixed_size(long_document, chunk_size=80, overlap=10)
    sentence_chunks = chunk_by_sentence(long_document, max_tokens=80)

    table = Table(title="Chunking comparison")
    table.add_column("Strategy",        style="cyan")
    table.add_column("# Chunks",        justify="right")
    table.add_column("Avg tokens/chunk", justify="right")

    avg_fixed    = sum(count_tokens(c) for c in fixed_chunks)    // len(fixed_chunks)
    avg_sentence = sum(count_tokens(c) for c in sentence_chunks) // len(sentence_chunks)

    table.add_row("Fixed-size (80 tok, 10 overlap)", str(len(fixed_chunks)),    str(avg_fixed))
    table.add_row("Sentence-aware (max 80 tok)",     str(len(sentence_chunks)), str(avg_sentence))
    console.print(table)

    # Show a sample chunk from each strategy
    console.print(Panel(fixed_chunks[2],    title="Fixed-size chunk [2]"))
    console.print(Panel(sentence_chunks[1], title="Sentence-aware chunk [1]"))

    # ── Technique 2: Compression ─────────────
    console.print("\n[bold cyan]Technique 2: Contextual compression[/bold cyan]")

    sample_chunk = sentence_chunks[0]
    compressed   = compress_chunk(sample_chunk, query)

    before_tokens = count_tokens(sample_chunk)
    after_tokens  = count_tokens(compressed)
    reduction     = round((1 - after_tokens / before_tokens) * 100)

    console.print(Panel(sample_chunk, title=f"Original chunk ({before_tokens} tokens)"))
    console.print(Panel(compressed,   title=f"Compressed chunk ({after_tokens} tokens, {reduction}% smaller)"))

    # ── Technique 3: Re-ranking ──────────────
    console.print("\n[bold cyan]Technique 3: Re-ranking by relevance[/bold cyan]")

    ranked = rerank_chunks(query, sentence_chunks[:4])

    rerank_table = Table(title=f"Re-ranked chunks for: '{query}'")
    rerank_table.add_column("Rank",  justify="right", style="cyan")
    rerank_table.add_column("Score", justify="right", style="green")
    rerank_table.add_column("Chunk preview (first 80 chars)")

    for rank, (score, chunk) in enumerate(ranked, start=1):
        rerank_table.add_row(str(rank), str(int(score)), chunk[:80] + "...")

    console.print(rerank_table)

    console.print("\n[bold green]✓ Module 4 complete![/bold green]")
    console.print("Next: [italic]python code/module5/lesson_agent_loop.py[/italic]\n")
