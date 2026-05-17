"""Tests for Module 9 — batch utilities, TokenPacer, parse_score."""
import time
import pytest
from tests.conftest import load_module, make_mock_response
from unittest.mock import MagicMock, patch

_rate  = load_module("code/module9/lesson3_rate_limits.py")
TokenPacer = _rate.TokenPacer

_batch = load_module("code/module9/lesson1_batch_api.py")
build_batch_requests = _batch.build_batch_requests
TEST_CASES           = _batch.TEST_CASES

_sol = load_module("solutions/module9/solution_batch_eval.py")
parse_score   = _sol.parse_score
build_requests = _sol.build_requests
SOL_TEST_CASES = _sol.TEST_CASES


class TestParseScore:
    def test_valid_decimal(self):
        assert parse_score("0.75") == 0.75

    def test_one_point_zero(self):
        assert parse_score("1.0") == 1.0

    def test_zero(self):
        assert parse_score("0.0") == 0.0

    def test_with_whitespace(self):
        assert parse_score("  0.5  ") == 0.5

    def test_invalid_string_returns_zero(self):
        assert parse_score("abc") == 0.0

    def test_empty_string_returns_zero(self):
        assert parse_score("") == 0.0

    def test_sentence_returns_zero(self):
        assert parse_score("the answer is 0.8") == 0.0

    def test_high_precision(self):
        assert abs(parse_score("0.8567") - 0.8567) < 1e-6

    def test_returns_float(self):
        assert isinstance(parse_score("0.9"), float)


class TestBuildBatchRequests:
    def setup_method(self):
        self.requests = build_batch_requests(TEST_CASES)

    def test_returns_list(self):
        assert isinstance(self.requests, list)

    def test_one_request_per_test_case(self):
        assert len(self.requests) == len(TEST_CASES)

    def test_each_request_has_custom_id(self):
        for req in self.requests:
            assert "custom_id" in req
            assert isinstance(req["custom_id"], str)

    def test_each_request_has_params(self):
        for req in self.requests:
            assert "params" in req

    def test_params_has_required_fields(self):
        for req in self.requests:
            params = req["params"]
            assert "model" in params
            assert "max_tokens" in params
            assert "messages" in params

    def test_custom_ids_are_unique(self):
        ids = [r["custom_id"] for r in self.requests]
        assert len(ids) == len(set(ids))

    def test_messages_contain_question(self):
        for req, case in zip(self.requests, TEST_CASES):
            user_msg = req["params"]["messages"][0]["content"]
            assert case["question"] in user_msg


class TestBuildSolutionRequests:
    def setup_method(self):
        self.requests = build_requests(SOL_TEST_CASES)

    def test_three_requests_per_test_case(self):
        # faithfulness + relevance + precision = 3 per case
        assert len(self.requests) == len(SOL_TEST_CASES) * 3

    def test_custom_ids_encode_metric(self):
        ids = [r["custom_id"] for r in self.requests]
        metrics = ["faithfulness", "relevance", "precision"]
        for metric in metrics:
            assert any(metric in id_ for id_ in ids)

    def test_all_custom_ids_unique(self):
        ids = [r["custom_id"] for r in self.requests]
        assert len(ids) == len(set(ids))


class TestTokenPacer:
    def test_initial_tokens_used_is_zero(self):
        pacer = TokenPacer(tpm_limit=1000)
        assert pacer.tokens_used == 0

    def test_estimate_returns_int(self):
        pacer = TokenPacer()
        assert isinstance(pacer._estimate("hello"), int)

    def test_estimate_empty_string(self):
        pacer = TokenPacer()
        assert pacer._estimate("") == 0

    def test_estimate_scales_with_length(self):
        pacer = TokenPacer()
        short = pacer._estimate("hi")
        long_ = pacer._estimate("this is a much longer sentence with many words")
        assert long_ > short

    def test_estimate_approximates_chars_over_4(self):
        pacer = TokenPacer()
        text = "a" * 400
        assert pacer._estimate(text) == 100  # 400 // 4

    def test_maybe_reset_does_not_reset_fresh_window(self):
        pacer = TokenPacer()
        pacer.tokens_used = 500
        pacer._maybe_reset()
        assert pacer.tokens_used == 500

    def test_maybe_reset_resets_after_60s(self):
        pacer = TokenPacer()
        pacer.tokens_used = 500
        pacer.window_start = time.time() - 61  # simulate expired window
        pacer._maybe_reset()
        assert pacer.tokens_used == 0

    def test_custom_tpm_limit(self):
        pacer = TokenPacer(tpm_limit=500)
        assert pacer.tpm_limit == 500

    def test_default_tpm_limit_is_positive(self):
        pacer = TokenPacer()
        assert pacer.tpm_limit > 0
