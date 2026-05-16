# Context Engineering for AI — Codebase Guide

## What this repo is

A seven-module course on context engineering for large language models, using the Anthropic Python SDK (`anthropic` package). Each module has lesson code under `code/`, a solution under `solutions/`, and markdown notes under `Lessons/`.

## Running code

```bash
cp .env.example .env          # add your ANTHROPIC_API_KEY
pip install -r requirements.txt
python code/module1/lesson1_context_demo.py
python solutions/module7/solution_cwa_design.py
python final_project/research_assistant.py
```

## Module map

| # | Topic | Key file |
|---|-------|----------|
| 1 | Context design & economics | `code/module1/lesson1_context_demo.py` |
| 2 | Prompting (zero-shot → few-shot → advanced) | `code/module2/lesson1_zero_shot.py` |
| 3 | RAG pipeline | `code/module3/lesson1_rag_pipeline.py` |
| 4 | Token budget & compression | `code/module4/lesson3_token_budget.py` |
| 5 | Agentic ReAct loop + tool design | `code/module5/lesson_agent_loop.py` |
| 6 | Evaluation suite | `code/module6/lesson1_evaluation.py` |
| 7 | CWA (Context Window Architecture) | `code/module7/lesson4_cwa.py` |
| – | Final project (all 11 CWA layers) | `final_project/research_assistant.py` |

## Shared config

[config.py](config.py) — model names, RAG distance threshold, summarization trigger. Change model strings here once instead of editing individual files.

## Key design patterns in the code

- **CWA layers**: The 11-layer context structure is defined in `solutions/module7/solution_cwa_design.py` and fully assembled in `final_project/research_assistant.py`.
- **Prompt caching**: Stable system-prompt layers use `cache_control: {type: ephemeral}` to avoid rebilling on repeated turns. See `final_project/research_assistant.py → build_system_prompt()`.
- **RAG distance filtering**: `retrieve()` drops chunks with distance > `RAG_DISTANCE_THRESHOLD` (default 0.7) so irrelevant context is never injected.
- **Rolling summarization**: Conversation history is compressed with Haiku every `SUMMARIZE_AFTER_TURNS` (default 8) turns to stay within context limits.
- **Parallel evaluation**: `solutions/module6/solution_evaluation.py` runs all metric API calls concurrently via `ThreadPoolExecutor`.

## Dependencies note

- `anthropic>=0.40,<1.0` — pinned to avoid breaking API changes
- `ragas>=0.1.0,<0.2.0` — Ragas 0.2 has an incompatible API; pin to 0.1.x
- Optional: add `TAVILY_API_KEY` to `.env` and `pip install tavily-python` to enable real web search in the final project
