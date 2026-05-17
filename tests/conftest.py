"""
Shared pytest configuration: sys.path setup, env vars, fixtures, helpers.
All test files in this directory inherit these automatically.
"""
import os
import sys
import importlib.util
from unittest.mock import MagicMock

# ── Path setup ────────────────────────────────────────────────────────────
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO_ROOT)

# Provide a dummy API key so Anthropic() can be instantiated without a .env file.
# os.environ.setdefault does NOT overwrite a real key already in the environment.
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-sk-ant-testing-only")

# ── Mock heavy optional dependencies that may not be installed ────────────
# This lets lesson files be imported in tests without requiring chromadb /
# sentence-transformers / ragas to be installed in the current environment.
# Tests that actually exercise chromadb code are skipped separately.
_MOCK_IF_MISSING = [
    "chromadb",
    "chromadb.utils",
    "chromadb.utils.embedding_functions",
    "sentence_transformers",
    "ragas",
]
for _dep in _MOCK_IF_MISSING:
    if _dep not in sys.modules:
        try:
            __import__(_dep)
        except ImportError:
            sys.modules[_dep] = MagicMock()


# ── Module loader helper ──────────────────────────────────────────────────
def load_module(repo_relative_path: str):
    """
    Loads a .py file by path relative to the repo root and returns the module.
    Works for files that aren't part of a Python package (no __init__.py).
    """
    filepath = os.path.join(REPO_ROOT, repo_relative_path)
    name = repo_relative_path.replace("/", "_").replace(".py", "")
    spec = importlib.util.spec_from_file_location(name, filepath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── Mock response factory ────────────────────────────────────────────────
def make_text_block(text: str):
    block = MagicMock()
    block.text = text
    block.type = "text"
    return block


def make_mock_response(text: str = "0.8", stop_reason: str = "end_turn"):
    """Returns a minimal mock Anthropic MessageResponse."""
    resp = MagicMock()
    resp.content = [make_text_block(text)]
    resp.stop_reason = stop_reason
    resp.usage = MagicMock()
    resp.usage.input_tokens = 50
    resp.usage.output_tokens = 10
    return resp


# ── Shared fixtures ───────────────────────────────────────────────────────
import pytest

@pytest.fixture
def mock_client():
    """A mocked Anthropic client whose messages.create() returns '0.8'."""
    mc = MagicMock()
    mc.messages.create.return_value = make_mock_response("0.8")
    return mc


@pytest.fixture
def sample_docs():
    return [
        {"id": "d1", "content": "MAX_UPLOAD_SIZE controls the maximum file upload size in bytes."},
        {"id": "d2", "content": "Users upload files to cloud storage for sharing."},
        {"id": "d3", "content": "HTTP 429 Too Many Requests means the rate limit was exceeded."},
        {"id": "d4", "content": "Neural networks learn by adjusting weights via backpropagation."},
        {"id": "d5", "content": "Vector embeddings represent text as dense numeric arrays."},
    ]
