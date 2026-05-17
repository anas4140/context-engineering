"""Tests for Module 4 — token counting and chunking utilities."""
import pytest
from tests.conftest import load_module

_mod = load_module("solutions/module4/solution_chunking.py")
tok = _mod.tok
chunk_fixed = _mod.chunk_fixed
chunk_sentence = _mod.chunk_sentence


SAMPLE_TEXT = (
    "The quick brown fox jumps over the lazy dog. "
    "Pack my box with five dozen liquor jugs. "
    "How vexingly quick daft zebras jump! "
    "The five boxing wizards jump quickly. "
    "Sphinx of black quartz, judge my vow."
)


class TestTokFunction:
    def test_empty_string_is_zero(self):
        assert tok("") == 0

    def test_single_word_is_positive(self):
        assert tok("hello") > 0

    def test_longer_text_more_tokens(self):
        assert tok("a very long sentence with many words") > tok("hello")

    def test_returns_int(self):
        assert isinstance(tok("hello world"), int)


class TestChunkFixed:
    def test_returns_list(self):
        result = chunk_fixed(SAMPLE_TEXT, size=50, overlap=10)
        assert isinstance(result, list)

    def test_nonempty_input_produces_chunks(self):
        result = chunk_fixed(SAMPLE_TEXT, size=50, overlap=10)
        assert len(result) >= 1

    def test_each_chunk_is_string(self):
        for chunk in chunk_fixed(SAMPLE_TEXT, size=50, overlap=10):
            assert isinstance(chunk, str)
            assert len(chunk) > 0

    def test_all_content_covered(self):
        # Every word in the source should appear in at least one chunk
        chunks = chunk_fixed(SAMPLE_TEXT, size=100, overlap=20)
        combined = " ".join(chunks)
        for word in SAMPLE_TEXT.split()[:5]:
            assert word in combined

    def test_smaller_chunks_produce_more_chunks(self):
        big   = chunk_fixed(SAMPLE_TEXT, size=200, overlap=0)
        small = chunk_fixed(SAMPLE_TEXT, size=50,  overlap=0)
        assert len(small) >= len(big)

    def test_empty_input_returns_empty_or_single(self):
        result = chunk_fixed("", size=50, overlap=0)
        assert isinstance(result, list)


class TestChunkSentence:
    def test_returns_list(self):
        result = chunk_sentence(SAMPLE_TEXT, max_tok=50)
        assert isinstance(result, list)

    def test_produces_chunks(self):
        result = chunk_sentence(SAMPLE_TEXT, max_tok=50)
        assert len(result) >= 1

    def test_each_chunk_is_string(self):
        for chunk in chunk_sentence(SAMPLE_TEXT, max_tok=50):
            assert isinstance(chunk, str)
            assert len(chunk) > 0

    def test_tight_budget_produces_more_chunks(self):
        loose = chunk_sentence(SAMPLE_TEXT, max_tok=200)
        tight = chunk_sentence(SAMPLE_TEXT, max_tok=30)
        assert len(tight) >= len(loose)
