"""Tests for Module 12 — PromptRegistry and A/B testing utilities."""
import pytest
from tests.conftest import load_module, make_mock_response
from unittest.mock import MagicMock, patch

_v = load_module("code/module12/lesson1_prompt_versioning.py")
PromptVersion  = _v.PromptVersion
PromptRegistry = _v.PromptRegistry
eval_prompt    = _v.eval_prompt


class TestPromptVersion:
    def test_created_with_required_fields(self):
        p = PromptVersion(name="test", version="v1.0", system="You are helpful.")
        assert p.name    == "test"
        assert p.version == "v1.0"
        assert p.system  == "You are helpful."

    def test_defaults(self):
        p = PromptVersion(name="x", version="v1", system="sys")
        assert p.notes      == ""
        assert p.production is False
        assert p.created_at  != ""

    def test_production_flag(self):
        p = PromptVersion(name="x", version="v1", system="sys", production=True)
        assert p.production is True


class TestPromptRegistry:
    def setup_method(self):
        self.registry = PromptRegistry()
        self.v1 = PromptVersion("qa", "v1.0", "Be helpful.", production=True)
        self.v2 = PromptVersion("qa", "v2.0", "Be precise and cite sources.")
        self.registry.register(self.v1).register(self.v2)

    def test_register_returns_self(self):
        r = PromptRegistry()
        result = r.register(PromptVersion("x", "v1", "sys"))
        assert result is r

    def test_get_by_version(self):
        p = self.registry.get("qa", "v1.0")
        assert p is self.v1

    def test_get_nonexistent_returns_none(self):
        assert self.registry.get("qa", "v999") is None
        assert self.registry.get("missing", "v1") is None

    def test_get_production(self):
        prod = self.registry.get_production("qa")
        assert prod is self.v1
        assert prod.production is True

    def test_get_production_missing_returns_none(self):
        assert self.registry.get_production("nonexistent") is None

    def test_history_returns_all_versions(self):
        history = self.registry.history("qa")
        assert len(history) == 2

    def test_promote_changes_production(self):
        self.registry.promote("qa", "v2.0")
        assert self.registry.get("qa", "v2.0").production is True
        assert self.registry.get("qa", "v1.0").production is False

    def test_promote_demotes_others(self):
        # v1.0 starts as production
        self.registry.promote("qa", "v2.0")
        # only v2.0 should be production now
        prods = [p for p in self.registry.history("qa") if p.production]
        assert len(prods) == 1
        assert prods[0].version == "v2.0"


class TestEvalPrompt:
    def test_returns_float(self):
        ctx = patch("anthropic.Anthropic")
        mc  = MagicMock()
        mc.messages.create.return_value = make_mock_response("0.8")

        with ctx:
            _v.client = mc
            result = eval_prompt("You are helpful.", [
                {"question": "What?", "context": "Something."},
            ])
        assert isinstance(result, float)

    def test_aggregates_multiple_cases(self):
        mc = MagicMock()
        mc.messages.create.return_value = make_mock_response("0.6")
        _v.client = mc

        result = eval_prompt("system", [
            {"question": "Q1", "context": "C1"},
            {"question": "Q2", "context": "C2"},
            {"question": "Q3", "context": "C3"},
        ])
        assert isinstance(result, float)
        assert 0.0 <= result <= 1.0


class TestABTestingLogic:
    """Test pure utility functions from lesson2_ab_testing.py"""

    def setup_method(self):
        self._ab = load_module("code/module12/lesson2_ab_testing.py")

    def test_judge_returns_valid_winner(self):
        mc = MagicMock()
        mc.messages.create.return_value = make_mock_response("B")
        self._ab.client = mc
        result = self._ab.judge("answer a", "answer b", "question", "context")
        assert result in {"A", "B", "TIE"}

    def test_judge_handles_unexpected_response(self):
        mc = MagicMock()
        mc.messages.create.return_value = make_mock_response("neither")
        self._ab.client = mc
        result = self._ab.judge("a", "b", "q", "c")
        assert result in {"A", "B", "TIE"}
