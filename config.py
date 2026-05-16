"""
Shared configuration for all modules.
Change model names here once instead of hunting across files.
"""

# Fast, cheap model — used for evaluation scoring, summarization, simple tasks
MODEL_FAST = "claude-haiku-4-5-20251001"

# High-quality model — used for the final project and complex reasoning
MODEL_QUALITY = "claude-sonnet-4-6"

# RAG retrieval — chunks with distance above this threshold are discarded
RAG_DISTANCE_THRESHOLD = 0.7

# Conversation summarization — trigger when history exceeds this many turns
SUMMARIZE_AFTER_TURNS = 8
