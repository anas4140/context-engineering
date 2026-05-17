"""Tests for Module 10 — MCP server tool handlers and schema conversion."""
import pytest
import asyncio

mcp = pytest.importorskip("mcp", reason="mcp package not installed")

from tests.conftest import load_module

_server = load_module("code/module10/mcp_server.py")
list_tools = _server.list_tools
call_tool  = _server.call_tool

_client = load_module("code/module10/lesson1_mcp_client.py")
mcp_to_claude_tool = _client.mcp_to_claude_tool

_agent = load_module("solutions/module10/solution_mcp_agent.py")
mcp_to_claude_tool_sol = _agent.mcp_to_claude_tool


class TestListTools:
    def test_returns_three_tools(self):
        tools = asyncio.run(list_tools())
        assert len(tools) == 3

    def test_tool_names(self):
        tools = asyncio.run(list_tools())
        names = {t.name for t in tools}
        assert "calculator"   in names
        assert "word_count"   in names
        assert "unit_convert" in names

    def test_each_tool_has_description(self):
        tools = asyncio.run(list_tools())
        for t in tools:
            assert t.description and len(t.description) > 0

    def test_each_tool_has_input_schema(self):
        tools = asyncio.run(list_tools())
        for t in tools:
            assert t.inputSchema is not None
            assert t.inputSchema.get("type") == "object"

    def test_calculator_requires_expression(self):
        tools = asyncio.run(list_tools())
        calc = next(t for t in tools if t.name == "calculator")
        assert "expression" in calc.inputSchema.get("required", [])

    def test_word_count_requires_text(self):
        tools = asyncio.run(list_tools())
        wc = next(t for t in tools if t.name == "word_count")
        assert "text" in wc.inputSchema.get("required", [])


class TestCallToolCalculator:
    def _run(self, name, args):
        return asyncio.run(call_tool(name, args))

    def test_basic_addition(self):
        result = self._run("calculator", {"expression": "2 + 2"})
        assert result[0].text == "Result: 4"

    def test_sqrt(self):
        result = self._run("calculator", {"expression": "sqrt(144)"})
        assert result[0].text == "Result: 12.0"

    def test_exponentiation(self):
        result = self._run("calculator", {"expression": "2 ** 8"})
        assert result[0].text == "Result: 256"

    def test_returns_list(self):
        result = self._run("calculator", {"expression": "1 + 1"})
        assert isinstance(result, list)

    def test_result_has_text_content(self):
        result = self._run("calculator", {"expression": "5 * 5"})
        assert hasattr(result[0], "text")

    def test_invalid_expression_returns_error(self):
        result = self._run("calculator", {"expression": "bad syntax !!"})
        assert result[0].text.startswith("Error")

    def test_division_by_zero_returns_error(self):
        result = self._run("calculator", {"expression": "1/0"})
        assert result[0].text.startswith("Error")


class TestCallToolWordCount:
    def _run(self, name, args):
        return asyncio.run(call_tool(name, args))

    def test_basic_count(self):
        result = self._run("word_count", {"text": "hello world foo"})
        assert result[0].text == "Word count: 3"

    def test_single_word(self):
        result = self._run("word_count", {"text": "hello"})
        assert result[0].text == "Word count: 1"

    def test_empty_string(self):
        result = self._run("word_count", {"text": ""})
        assert result[0].text == "Word count: 0"

    def test_multiword_sentence(self):
        result = self._run("word_count", {"text": "the quick brown fox"})
        assert result[0].text == "Word count: 4"


class TestCallToolUnitConvert:
    def _run(self, name, args):
        return asyncio.run(call_tool(name, args))

    def test_celsius_to_fahrenheit_freezing(self):
        result = self._run("unit_convert", {"value": 0, "from_unit": "celsius", "to_unit": "fahrenheit"})
        assert "32.0" in result[0].text

    def test_celsius_to_fahrenheit_boiling(self):
        result = self._run("unit_convert", {"value": 100, "from_unit": "celsius", "to_unit": "fahrenheit"})
        assert "212.0" in result[0].text

    def test_km_to_miles(self):
        result = self._run("unit_convert", {"value": 1, "from_unit": "km", "to_unit": "miles"})
        assert "0.621" in result[0].text

    def test_kg_to_lbs(self):
        result = self._run("unit_convert", {"value": 1, "from_unit": "kg", "to_unit": "lbs"})
        assert "2.204" in result[0].text

    def test_unsupported_conversion_returns_message(self):
        result = self._run("unit_convert", {"value": 1, "from_unit": "parsec", "to_unit": "furlongs"})
        assert "Unsupported" in result[0].text

    def test_fahrenheit_to_celsius(self):
        result = self._run("unit_convert", {"value": 32, "from_unit": "fahrenheit", "to_unit": "celsius"})
        assert "0.0" in result[0].text


class TestCallToolUnknown:
    def test_unknown_tool_returns_error_message(self):
        result = asyncio.run(call_tool("totally_unknown_tool", {}))
        assert "Unknown tool" in result[0].text


class TestMcpToClaudeTool:
    def setup_method(self):
        tools = asyncio.run(list_tools())
        self.calc_mcp = next(t for t in tools if t.name == "calculator")

    def test_returns_dict(self):
        result = mcp_to_claude_tool(self.calc_mcp)
        assert isinstance(result, dict)

    def test_has_name(self):
        result = mcp_to_claude_tool(self.calc_mcp)
        assert result["name"] == "calculator"

    def test_has_description(self):
        result = mcp_to_claude_tool(self.calc_mcp)
        assert "description" in result
        assert len(result["description"]) > 0

    def test_has_input_schema(self):
        result = mcp_to_claude_tool(self.calc_mcp)
        assert "input_schema" in result
        assert result["input_schema"]["type"] == "object"

    def test_solution_converter_matches_lesson_converter(self):
        result_lesson = mcp_to_claude_tool(self.calc_mcp)
        result_sol    = mcp_to_claude_tool_sol(self.calc_mcp)
        assert result_lesson["name"] == result_sol["name"]
        assert result_lesson["input_schema"] == result_sol["input_schema"]
