"""
Tests for the calculator() pure function.
Same implementation appears in multiple lesson files; tested via the
canonical version in code/module5/lesson_agent_loop.py.
"""
import importlib.util
import os
import pytest
from tests.conftest import REPO_ROOT, load_module

_mod = load_module("code/module5/lesson_agent_loop.py")
calculator = _mod.calculator
execute_tool = _mod.execute_tool
TOOLS = _mod.TOOLS


class TestCalculatorBasicArithmetic:
    def test_addition(self):
        assert calculator("2 + 2") == "Result: 4"

    def test_subtraction(self):
        assert calculator("10 - 3") == "Result: 7"

    def test_multiplication(self):
        assert calculator("6 * 7") == "Result: 42"

    def test_division(self):
        result = calculator("10 / 4")
        assert result == "Result: 2.5"

    def test_integer_division(self):
        result = calculator("9 // 3")
        assert result == "Result: 3"

    def test_exponentiation(self):
        assert calculator("2 ** 10") == "Result: 1024"

    def test_modulo(self):
        assert calculator("17 % 5") == "Result: 2"

    def test_order_of_operations(self):
        assert calculator("2 + 3 * 4") == "Result: 14"

    def test_parentheses(self):
        assert calculator("(2 + 3) * 4") == "Result: 20"


class TestCalculatorMathFunctions:
    def test_sqrt(self):
        assert calculator("sqrt(144)") == "Result: 12.0"

    def test_sqrt_of_2(self):
        result = calculator("sqrt(2)")
        assert result.startswith("Result:")
        assert abs(float(result.split(": ")[1]) - 1.41421) < 0.0001

    def test_abs_positive(self):
        assert calculator("abs(5)") == "Result: 5"

    def test_abs_negative(self):
        assert calculator("abs(-7)") == "Result: 7"

    def test_floor(self):
        assert calculator("floor(3.9)") == "Result: 3"

    def test_ceil(self):
        assert calculator("ceil(3.1)") == "Result: 4"

    def test_pi(self):
        result = calculator("pi")
        assert result.startswith("Result:")
        assert abs(float(result.split(": ")[1]) - 3.14159) < 0.0001

    def test_log(self):
        result = calculator("log(1)")
        assert result == "Result: 0.0"

    def test_complex_expression(self):
        # (1.5 - 1.2) / 1.2 * 100  ≈ 25.0
        result = calculator("(1.5 - 1.2) / 1.2 * 100")
        assert result.startswith("Result:")
        assert abs(float(result.split(": ")[1]) - 25.0) < 0.001


class TestCalculatorErrorHandling:
    def test_invalid_syntax_returns_error(self):
        result = calculator("2 +* 3")
        assert result.startswith("Error")

    def test_division_by_zero_returns_error(self):
        result = calculator("1 / 0")
        assert result.startswith("Error")

    def test_undefined_name_returns_error(self):
        result = calculator("undefined_var + 1")
        assert result.startswith("Error")

    def test_empty_string_returns_error(self):
        result = calculator("")
        assert result.startswith("Error")


class TestCalculatorSecurity:
    def test_builtins_blocked(self):
        # __builtins__ is set to {} — import should not work
        result = calculator("__import__('os').system('echo hacked')")
        assert result.startswith("Error")

    def test_open_blocked(self):
        result = calculator("open('/etc/passwd').read()")
        assert result.startswith("Error")

    def test_exec_blocked(self):
        result = calculator("exec('import os')")
        assert result.startswith("Error")


class TestExecuteTool:
    def test_dispatches_calculator(self):
        result = execute_tool("calculator", {"expression": "3 * 3"})
        assert result == "Result: 9"

    def test_unknown_tool_returns_error(self):
        result = execute_tool("nonexistent_tool", {})
        assert "unknown" in result.lower() or "error" in result.lower()

    def test_calculator_bad_args_returns_error(self):
        result = execute_tool("calculator", {"expression": "bad syntax @@"})
        assert result.startswith("Error")


class TestToolSchemas:
    def test_tools_is_a_list(self):
        assert isinstance(TOOLS, list)
        assert len(TOOLS) > 0

    def test_each_tool_has_required_keys(self):
        for tool in TOOLS:
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool

    def test_each_tool_name_is_string(self):
        for tool in TOOLS:
            assert isinstance(tool["name"], str)
            assert len(tool["name"]) > 0

    def test_input_schema_has_type_object(self):
        for tool in TOOLS:
            assert tool["input_schema"]["type"] == "object"
            assert "properties" in tool["input_schema"]
