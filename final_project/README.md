# Final Project — AI Research Assistant

A complete, interactive AI Research Assistant that demonstrates all 11 CWA layers, a ChromaDB RAG pipeline, a function-calling agent, multi-turn conversation memory, and per-response evaluation.

---

## Files in This Directory

| File | Purpose |
|---|---|
| `research_assistant.py` | Main interactive assistant — run this |
| `evaluate.py` | Automated evaluation suite — run to score your implementation |

---

## Quick Start

```bash
# From the repo root
python final_project/research_assistant.py
```

Type research questions at the prompt. The assistant will:
- Retrieve relevant chunks from the built-in climate science knowledge base
- Call tools (web search, calculator) when needed
- Generate a cited Markdown response
- Display a faithfulness score after each answer

Type `clear` to reset the conversation. Type `quit` to exit.

---

## Running the Evaluation Suite

```bash
python final_project/evaluate.py
```

This runs 5 pre-defined test queries and prints a scored table with faithfulness, relevance, and context precision for each response. Any response below 0.7 faithfulness is flagged.

---

## Extending for the Final Project Deliverables

Open `research_assistant.py` and make the following changes:

### Deliverable 1 — Add Your Own Documents
Find `RESEARCH_DOCUMENTS` near the top of the file. Add 5+ new documents with your chosen domain. Each needs `id`, `source`, `page`, and `content`.

### Deliverable 2 — Rewrite the System Prompt
Find `build_system_prompt()`. Rewrite the Layer 1 persona, Layer 2 safety rules, Layer 3 domain context, and Layer 10 format instructions for your domain.

### Deliverable 3 — Add a New Tool
Add an entry to `TOOLS` (JSON Schema) and `TOOL_FUNCTIONS` (Python function). Test it with 3 queries.

### Deliverable 4 — Conversation Summarisation
Add this function and call it inside `run_research_assistant()` every 6 turns:

```python
def summarise_conversation(history: list[dict]) -> str:
    """Compresses old turns into a 3-sentence summary."""
    history_text = "\n".join(
        f"{m['role'].upper()}: {m['content'][:200]}"
        for m in history
        if isinstance(m["content"], str)
    )
    response = client.messages.create(
        model="claude-haiku-4-5-20251001", max_tokens=200,
        messages=[{"role": "user", "content":
            f"Summarise this conversation in 3 sentences:\n\n{history_text}"}]
    )
    return response.content[0].text
```

### Deliverable 5 — Evaluation Suite
Run `python final_project/evaluate.py`. Add 5 test queries relevant to your domain to the `TEST_QUERIES` list in that file.

---

## CWA Layer Map

| Layer | Where it lives in the code |
|---|---|
| 1 — Identity | `build_system_prompt()` — L1 variable |
| 2 — Safety | `build_system_prompt()` — L2 variable |
| 3 — Curated knowledge | `build_system_prompt()` — L3 variable |
| 4 — Task state | Implicit in conversation topic |
| 5 — Long-term memory | `build_system_prompt()` — L5 variable |
| 6 — Short-term memory | `conversation_history` list |
| 7 — Tool definitions | `TOOLS` list |
| 8 — Dynamic RAG | `retrieve()` → injected in final user message |
| 9 — Tool results | `tool_results` list in agent loop |
| 10 — Format | `build_system_prompt()` — L10 variable |
| 11 — User query | Last item in `messages` |
