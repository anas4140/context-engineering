"""
Shared configuration for all modules.
Change model names here once instead of hunting across files.
"""

# Fast, cheap model — used for evaluation scoring, summarization, simple tasks
MODEL_FAST = "claude-haiku-4-5-20251001"

# High-quality model — used for the final project and complex reasoning
MODEL_QUALITY = "claude-sonnet-4-6"

# Extended thinking model — supports thinking token budgets (Module 8)
MODEL_THINKING = "claude-opus-4-7"

# RAG retrieval — chunks with distance above this threshold are discarded
RAG_DISTANCE_THRESHOLD = 0.7

# Conversation summarization — trigger when history exceeds this many turns
SUMMARIZE_AFTER_TURNS = 8

# Extended thinking — default token budget for reasoning scratchpad
THINKING_BUDGET_DEFAULT = 8000

# Batch API — seconds to wait between status polls
BATCH_POLL_INTERVAL = 10
