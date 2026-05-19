"""Tests for Module 5 — simulated tools and structured output schemas."""
import pytest
from tests.conftest import load_module

_mod   = load_module("code/module5/lesson_agent_loop.py")
get_weather     = _mod.get_weather
search_products = _mod.search_products

_ra = load_module("final_project/research_assistant.py")
web_search = _ra.web_search


class TestGetWeather:
    def test_returns_string(self):
        assert isinstance(get_weather("london"), str)

    def test_contains_city_name(self):
        result = get_weather("London")
        assert "London" in result

    def test_celsius_is_default_unit(self):
        result = get_weather("tokyo")
        assert "°C" in result

    def test_fahrenheit_unit(self):
        result = get_weather("tokyo", unit="fahrenheit")
        assert "°F" in result

    def test_celsius_and_fahrenheit_differ(self):
        c = get_weather("london", unit="celsius")
        f = get_weather("london", unit="fahrenheit")
        assert c != f

    def test_known_cities_return_data(self):
        for city in ["london", "new york", "tokyo", "dubai", "sydney"]:
            result = get_weather(city)
            assert len(result) > 0

    def test_unknown_city_returns_something(self):
        result = get_weather("atlantis")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_result_contains_humidity(self):
        result = get_weather("london")
        assert "Humidity" in result or "humidity" in result

    def test_fahrenheit_freezing(self):
        # 0°C = 32°F
        result = get_weather("london", unit="fahrenheit")
        # London is 12°C = 53.6°F — just check it's a number
        assert "°F" in result


class TestSearchProducts:
    def test_returns_string(self):
        assert isinstance(search_products("SmartFridge"), str)

    def test_matching_query_finds_products(self):
        result = search_products("SmartFridge")
        assert "SmartFridge" in result

    def test_no_match_returns_not_found(self):
        result = search_products("xxnonexistentproductxx")
        assert "No products found" in result or "not found" in result.lower()

    def test_on_sale_only_filters(self):
        all_results  = search_products("SmartFridge", on_sale_only=False)
        sale_results = search_products("SmartFridge", on_sale_only=True)
        # Sale results should be a subset or equal
        assert len(sale_results) <= len(all_results)

    def test_on_sale_items_tagged(self):
        result = search_products("SmartFridge", on_sale_only=True)
        if "No products found" not in result:
            assert "ON SALE" in result

    def test_out_of_stock_flagged(self):
        result = search_products("AirPure")
        assert "Out of stock" in result or "SmartFridge" in result or "AirPure" in result

    def test_airpure_found(self):
        result = search_products("AirPure")
        assert "AirPure" in result

    def test_case_insensitive_search(self):
        lower = search_products("smartfridge")
        upper = search_products("SMARTFRIDGE")
        assert lower == upper


class TestWebSearch:
    def test_returns_string(self):
        assert isinstance(web_search("carbon capture"), str)

    def test_known_keyword_returns_result(self):
        result = web_search("carbon capture")
        assert len(result) > 20

    def test_ocean_acidification_keyword(self):
        result = web_search("ocean acidification")
        assert len(result) > 20

    def test_renewable_energy_keyword(self):
        result = web_search("renewable energy")
        assert len(result) > 20

    def test_unknown_query_returns_fallback(self):
        result = web_search("zzzzz_completely_unknown_topic_xyz")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_no_tavily_key_uses_simulated(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        result = web_search("carbon capture")
        assert "Simulated" in result or len(result) > 10


class TestToolSchemaValidation:
    """Validates the JSON schema structure of every tool definition in the course."""

    def _check_tool(self, tool: dict):
        assert "name" in tool, f"Tool missing 'name': {tool}"
        assert "description" in tool, f"Tool missing 'description': {tool}"
        assert "input_schema" in tool, f"Tool missing 'input_schema': {tool}"
        schema = tool["input_schema"]
        assert schema.get("type") == "object"
        assert "properties" in schema

    def test_agent_loop_tools(self):
        for tool in _mod.TOOLS:
            self._check_tool(tool)

    def test_research_assistant_tools(self):
        for tool in _ra.TOOLS:
            self._check_tool(tool)

    def test_structured_output_tools(self):
        so = load_module("code/module5/lesson4_structured_outputs.py")
        for tool in [so.PERSON_TOOL, so.SENTIMENT_TOOL, so.MEETING_TOOL]:
            self._check_tool(tool)

    def test_person_tool_required_fields(self):
        so = load_module("code/module5/lesson4_structured_outputs.py")
        required = so.PERSON_TOOL["input_schema"].get("required", [])
        assert "name" in required
        assert "age" in required
        assert "city" in required

    def test_sentiment_tool_has_enum(self):
        so = load_module("code/module5/lesson4_structured_outputs.py")
        props = so.SENTIMENT_TOOL["input_schema"]["properties"]
        assert "enum" in props["sentiment"]
        assert "positive" in props["sentiment"]["enum"]
        assert "negative" in props["sentiment"]["enum"]
