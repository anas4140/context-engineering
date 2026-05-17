"""Tests for config.py — all constants exist and have sensible values."""
import pytest
from tests.conftest import REPO_ROOT
import sys
sys.path.insert(0, REPO_ROOT)

import config


class TestModelConstants:
    def test_model_fast_is_string(self):
        assert isinstance(config.MODEL_FAST, str)

    def test_model_quality_is_string(self):
        assert isinstance(config.MODEL_QUALITY, str)

    def test_model_thinking_is_string(self):
        assert isinstance(config.MODEL_THINKING, str)

    def test_model_fast_contains_claude(self):
        assert "claude" in config.MODEL_FAST.lower()

    def test_model_quality_contains_claude(self):
        assert "claude" in config.MODEL_QUALITY.lower()

    def test_model_thinking_contains_claude(self):
        assert "claude" in config.MODEL_THINKING.lower()

    def test_all_three_models_are_distinct(self):
        models = {config.MODEL_FAST, config.MODEL_QUALITY, config.MODEL_THINKING}
        assert len(models) == 3

    def test_model_fast_is_haiku(self):
        assert "haiku" in config.MODEL_FAST.lower()

    def test_model_quality_is_sonnet(self):
        assert "sonnet" in config.MODEL_QUALITY.lower()

    def test_model_thinking_is_opus(self):
        assert "opus" in config.MODEL_THINKING.lower()


class TestRagThresholds:
    def test_rag_distance_threshold_is_float(self):
        assert isinstance(config.RAG_DISTANCE_THRESHOLD, float)

    def test_rag_distance_threshold_between_0_and_1(self):
        assert 0.0 < config.RAG_DISTANCE_THRESHOLD <= 1.0

    def test_summarize_after_turns_is_int(self):
        assert isinstance(config.SUMMARIZE_AFTER_TURNS, int)

    def test_summarize_after_turns_positive(self):
        assert config.SUMMARIZE_AFTER_TURNS >= 1


class TestThinkingAndBatchConstants:
    def test_thinking_budget_default_is_int(self):
        assert isinstance(config.THINKING_BUDGET_DEFAULT, int)

    def test_thinking_budget_at_least_minimum(self):
        # Anthropic requires minimum 1024 thinking tokens
        assert config.THINKING_BUDGET_DEFAULT >= 1024

    def test_batch_poll_interval_is_int(self):
        assert isinstance(config.BATCH_POLL_INTERVAL, int)

    def test_batch_poll_interval_positive(self):
        assert config.BATCH_POLL_INTERVAL >= 1

    def test_all_expected_attributes_exist(self):
        expected = [
            "MODEL_FAST", "MODEL_QUALITY", "MODEL_THINKING",
            "RAG_DISTANCE_THRESHOLD", "SUMMARIZE_AFTER_TURNS",
            "THINKING_BUDGET_DEFAULT", "BATCH_POLL_INTERVAL",
        ]
        for attr in expected:
            assert hasattr(config, attr), f"config.{attr} is missing"
