"""Tests for Module 11 — async utilities and concurrent agent helpers."""
import asyncio
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from tests.conftest import load_module, make_mock_response, REPO_ROOT
import os

_m11 = load_module("code/module11/lesson2_concurrent_agents.py")
subagent             = _m11.subagent
gather_with_fallbacks = _m11.gather_with_fallbacks
score_metric         = _m11.score_metric


class TestSubagent:
    def test_returns_string(self):
        ctx, mc = patch("anthropic.AsyncAnthropic"), MagicMock()
        mock_response        = MagicMock()
        mock_response.content = [MagicMock(text="hello")]
        mc.messages.create   = AsyncMock(return_value=mock_response)

        async def run():
            _m11.async_client = mc
            return await subagent("test", "You are helpful.", "Say hello.", timeout=30.0)

        result = asyncio.run(run())
        assert isinstance(result, str)

    def test_timeout_returns_message(self):
        async def slow(): await asyncio.sleep(10)
        mc = MagicMock()
        mc.messages.create = AsyncMock(side_effect=asyncio.TimeoutError)

        async def run():
            _m11.async_client = mc
            return await subagent("slow", "system", "task", timeout=0.001)

        result = asyncio.run(run())
        assert "timed out" in result.lower() or isinstance(result, str)


class TestGatherWithFallbacks:
    def test_successful_tasks(self):
        async def good(): return "ok"
        results = asyncio.run(gather_with_fallbacks([good(), good()]))
        assert results == ["ok", "ok"]

    def test_failed_task_returns_none(self):
        async def good():  return "ok"
        async def bad():   raise ValueError("boom")
        results = asyncio.run(gather_with_fallbacks([good(), bad(), good()]))
        assert results[0] == "ok"
        assert results[1] is None
        assert results[2] == "ok"

    def test_all_failed_returns_all_none(self):
        async def bad(): raise RuntimeError("fail")
        results = asyncio.run(gather_with_fallbacks([bad(), bad()]))
        assert all(r is None for r in results)

    def test_empty_returns_empty(self):
        assert asyncio.run(gather_with_fallbacks([])) == []


class TestScoreMetric:
    def test_returns_float(self):
        mc = MagicMock()
        mock_resp        = MagicMock()
        mock_resp.content = [MagicMock(text="0.85")]
        mc.messages.create = AsyncMock(return_value=mock_resp)

        async def run():
            _m11.async_client = mc
            return await score_metric("faithfulness", "answer", "context")

        result = asyncio.run(run())
        assert isinstance(result, float)

    def test_invalid_response_returns_zero(self):
        mc = MagicMock()
        mock_resp        = MagicMock()
        mock_resp.content = [MagicMock(text="not a number")]
        mc.messages.create = AsyncMock(return_value=mock_resp)

        async def run():
            _m11.async_client = mc
            return await score_metric("relevance", "answer", "question")

        result = asyncio.run(run())
        assert result == 0.0

    def test_float_between_0_and_1(self):
        mc = MagicMock()
        mock_resp        = MagicMock()
        mock_resp.content = [MagicMock(text="0.75")]
        mc.messages.create = AsyncMock(return_value=mock_resp)

        async def run():
            _m11.async_client = mc
            return await score_metric("faithfulness", "a", "b")

        result = asyncio.run(run())
        assert 0.0 <= result <= 1.0
