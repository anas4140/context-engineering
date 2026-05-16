# Final Project: AI Research Assistant

> Apply every skill from the course to build a production-grade, context-aware AI research assistant.

---

## Overview

You will build a complete AI Research Assistant using all 11 layers of the **Context Window Architecture (CWA)** defined in Module 7. A working reference implementation is provided in [`final_project/research_assistant.py`](final_project/research_assistant.py) — study it, then extend it with the tasks below.

---

## CWA Layer Reference

Before starting, review [`code/module7/lesson4_cwa.py`](code/module7/lesson4_cwa.py) which defines all 11 layers. Here is a quick reference:

| Layer | Name | Role |
|---|---|---|
| **1** | Instructions (System Identity) | Persona, primary goal, non-negotiable rules |
| **2** | Safety & Guardrails | What the model must NEVER do |
| **3** | Curated Knowledge (Static RAG) | Pre-vetted domain facts, always included |
| **4** | Task / Goal State | Current task and progress |
| **5** | Long-term Memory | Summarised user preferences from past sessions |
| **6** | Short-term Memory (Conversation Summary) | Running summary of the current conversation |
| **7** | Tool Definitions | JSON Schema descriptions of all available tools |
| **8** | Dynamic RAG Results | Retrieved chunks for the current query |
| **9** | Tool Results / Observations | Output from tool calls (injected after execution) |
| **10** | Response Format Instructions | Exact output structure the model must follow |
| **11** | User's Latest Query | The current user message |

---

## Deliverables

Your final project must include all of the following:

### Deliverable 1 — Populated Knowledge Base (Layer 3 + 8)

Add at least **5 new documents** to the `RESEARCH_DOCUMENTS` list in `research_assistant.py`. Your documents must:
- Come from a coherent domain of your choice (not necessarily climate science)
- Include realistic `source` (filename) and `page` metadata
- Be substantive enough to support multi-turn Q&A

### Deliverable 2 — Custom System Prompt (Layers 1, 2, 3, 5, 10)

Rewrite the `build_system_prompt()` function to reflect your chosen domain. Your system prompt must include:
- **Layer 1**: A persona specific to your domain (not "climate science assistant")
- **Layer 2**: At least 3 domain-specific safety rules
- **Layer 3**: At least 2 curated domain facts that are always injected
- **Layer 10**: A response format with at least 3 specific structural requirements

### Deliverable 3 — New Tool (Layer 7 + 9)

Add at least one new tool to the `TOOLS` list and implement its Python function. The tool must:
- Have a complete JSON Schema with a description, all parameters described, and correct `required` fields
- Do something useful for your domain (e.g. `convert_units`, `lookup_stock_price`, `format_citation`)
- Be tested with at least 3 queries that trigger it

### Deliverable 4 — Conversation Memory (Layer 6)

The reference implementation keeps full conversation history. Extend it to:
- Automatically **summarise** the conversation every 6 turns (to save tokens)
- Inject the summary as a "conversation so far" block at the top of the user message
- This prevents context window overflow in long research sessions

Use this function signature:
```python
def summarise_conversation(history: list[dict]) -> str:
    """
    Takes the full conversation history and returns a 2-3 sentence summary.
    Called automatically every 6 turns.
    """
    ...
```

### Deliverable 5 — Evaluation Suite (Module 6 skills)

Write a script `final_project/evaluate.py` that:
1. Runs at least **5 test queries** against your assistant
2. Scores each response on faithfulness, answer relevance, and context precision
3. Prints a summary table (see `code/module6/lesson1_evaluation.py` for the pattern)
4. Flags any response with a faithfulness score below 0.7

---

## Grading Rubric

| Criterion | Points |
|---|---|
| Knowledge base: 5+ relevant documents with metadata | 10 |
| System prompt: correct Layer 1, 2, 3, 5, 10 usage | 20 |
| New tool: complete JSON Schema + working implementation | 20 |
| Conversation summarisation implemented correctly | 20 |
| Evaluation suite runs and produces a scored table | 20 |
| Code runs without errors end-to-end | 10 |
| **Total** | **100** |

---

## Getting Started

```bash
# Run the reference implementation to see what you're building toward
python final_project/research_assistant.py

# Then open the file and start extending it:
# 1. Replace RESEARCH_DOCUMENTS with your own domain
# 2. Rewrite build_system_prompt() for your persona
# 3. Add your new tool to TOOLS and TOOL_FUNCTIONS
# 4. Implement summarise_conversation()
# 5. Write final_project/evaluate.py
```

---

## Tips

- **Start with Deliverable 1** — good documents make everything else easier.
- **Test your tool definition** using `solutions/module5/solution_tool_definition.py` as a template.
- **The evaluation suite is your quality gate** — if faithfulness scores are low, improve your RAG prompt.
- Refer to [`GLOSSARY.md`](GLOSSARY.md) for any unfamiliar terms.
