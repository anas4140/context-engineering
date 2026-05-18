# Context Engineering for AI — Codebase Guide

## What this repo is

A twelve-module course on context engineering for large language models, using the Anthropic Python SDK (`anthropic` package). Each module has lesson code under `code/`, a solution under `solutions/`, and markdown notes under `Lessons/`.

## Running code

```bash
cp .env.example .env          # add your ANTHROPIC_API_KEY
pip install -r requirements.txt
python code/module1/lesson1_context_demo.py
python solutions/module7/solution_cwa_design.py
python final_project/research_assistant.py
```

## Module map

| # | Topic | Key lesson file | Key solution |
|---|-------|-----------------|--------------|
| 1 | Context design & economics | `code/module1/lesson1_context_demo.py` | `solutions/module1/solution_context_design.py` |
| 2 | Prompting (zero-shot → few-shot → advanced) | `code/module2/lesson1_zero_shot.py` | `solutions/module2/solution_few_shot.py` |
| 3 | RAG pipeline + **Hybrid Search** (Lesson 5) | `code/module3/lesson1_rag_pipeline.py` | `solutions/module3/solution_hybrid_search.py` |
| 4 | Token budget & compression | `code/module4/lesson3_token_budget.py` | `solutions/module4/solution_chunking.py` |
| 5 | Agentic ReAct + tool design + **Structured Outputs** (Lesson 4) | `code/module5/lesson_agent_loop.py` | `solutions/module5/solution_structured_outputs.py` |
| 6 | Evaluation suite | `code/module6/lesson1_evaluation.py` | `solutions/module6/solution_evaluation.py` |
| 7 | CWA + multimodal + **Files API** (Lesson 5) | `code/module7/lesson4_cwa.py` | `solutions/module7/solution_files_api.py` |
| 8 | **Extended Thinking** | `code/module8/lesson1_extended_thinking.py` | `solutions/module8/solution_extended_thinking.py` |
| 9 | **Production at Scale** (Batch API, Streaming, Rate Limits) | `code/module9/lesson1_batch_api.py` | `solutions/module9/solution_batch_eval.py` |
| 10 | **Model Context Protocol (MCP)** | `code/module10/lesson1_mcp_client.py` | `solutions/module10/solution_mcp_agent.py` |
| 11 | **Async & Concurrent Patterns** | `code/module11/lesson1_async_basics.py` | `solutions/module11/solution_async_agent.py` |
| 12 | **Prompt Versioning & A/B Testing** | `code/module12/lesson1_prompt_versioning.py` | `solutions/module12/solution_ab_testing.py` |
| — | Final project (all 11 CWA layers) | `final_project/research_assistant.py` | — |

## Shared config

[config.py](config.py) — model names, RAG distance threshold, summarization trigger, thinking budget, batch poll interval. Change model strings here once instead of editing individual files.

```python
MODEL_FAST      = "claude-haiku-4-5-20251001"   # eval, scoring, simple tasks
MODEL_QUALITY   = "claude-sonnet-4-6"            # final project
MODEL_THINKING  = "claude-opus-4-7"              # Module 8 extended thinking
```

## Key design patterns in the code

**Prompt caching** — Stable system-prompt layers use `cache_control: {type: ephemeral}`. See `final_project/research_assistant.py → build_system_prompt()` and `solutions/module7/solution_cwa_design.py`.

**Hybrid RAG** — `code/module3/lesson3_hybrid_search.py` combines ChromaDB dense search with BM25 sparse retrieval, fused via Reciprocal Rank Fusion. RAG chunks are also filtered by `RAG_DISTANCE_THRESHOLD`.

**Structured outputs** — `code/module5/lesson3_structured_outputs.py` uses `tool_choice: {type: tool}` to force schema-conforming JSON with no string parsing.

**Extended thinking** — `code/module8/` demos the `thinking: {type: enabled, budget_tokens: N}` parameter on `claude-opus-4-7`. Budget utilisation is measured to avoid over-allocation.

**Batch API** — `code/module9/lesson1_batch_api.py` and `solutions/module9/solution_batch_eval.py` submit multiple requests at 50% cost, poll for completion, and stream results.

**Streaming** — `code/module9/lesson2_streaming.py` covers text streaming, event-level streaming, and streaming tool use with partial JSON accumulation.

**Rate limiting** — `code/module9/lesson3_rate_limits.py` uses `tenacity` for exponential back-off, reads `Retry-After` headers, and tracks TPM usage.

**MCP** — `code/module10/mcp_server.py` is a standalone MCP server (3 tools). `code/module10/lesson1_mcp_client.py` connects via stdio, discovers tools dynamically, and runs a full ReAct loop through the MCP session.

**Files API** — `code/module7/lesson5_files_api.py` uploads text/PDFs once and references them by `file_id` in `client.beta.messages.create()` with `betas=["files-api-2025-04-14"]`.

**Rolling summarization** — Conversation history in `final_project/research_assistant.py` is compressed with Haiku every `SUMMARIZE_AFTER_TURNS` turns.

**Async concurrency** — `code/module11/` uses `anthropic.AsyncAnthropic` with `asyncio.gather` for concurrent agent calls and `asyncio.Semaphore` for rate-limit-safe batching.

**Prompt versioning** — `code/module12/lesson1_prompt_versioning.py` implements a `PromptRegistry` with version tagging, production promotion gating, and quality-delta checks.

**A/B testing** — `code/module12/lesson2_ab_testing.py` runs controlled prompt comparisons using LLM-as-judge, reporting win/loss/tie breakdown and a promotion recommendation.

## CI / Tests

- `python3 -m pytest tests/` — 268 unit tests, all pure (no API key needed), under 2s
- `.github/workflows/run-tests.yml` — runs on every push to `main`
- `.github/workflows/deploy-docs.yml` — builds Docusaurus site and deploys to GitHub Pages

## Dependencies note

- `anthropic>=0.40,<1.0` — pinned to avoid breaking API changes
- `ragas>=0.1.0,<0.2.0` — Ragas 0.2 has an incompatible API
- `rank-bm25>=0.2.2` — BM25 sparse retrieval for Module 3 hybrid search
- `mcp>=1.0.0` — MCP client/server library for Module 10
- Optional: add `TAVILY_API_KEY` to `.env` + `pip install tavily-python` for real web search in the final project
