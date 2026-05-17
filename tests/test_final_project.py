"""
Tests for final_project/ — web_search, execute_tool, build_system_prompt,
and the RAG retrieval pipeline (chromadb-free paths).
"""
import pytest
from tests.conftest import load_module

_ra = load_module("final_project/research_assistant.py")
web_search          = _ra.web_search
calculator          = _ra.calculator
execute_tool        = _ra.execute_tool
build_system_prompt = _ra.build_system_prompt
TOOLS               = _ra.TOOLS
RESEARCH_DOCUMENTS  = _ra.RESEARCH_DOCUMENTS

_ev = load_module("final_project/evaluate.py")
keyword_check = _ev.keyword_check


class TestWebSearchFallback:
    def test_returns_string(self):
        assert isinstance(web_search("carbon capture"), str)

    def test_carbon_capture_hits_simulated(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        result = web_search("carbon capture")
        assert len(result) > 20

    def test_ocean_acidification_hits_simulated(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        result = web_search("ocean acidification")
        assert len(result) > 20

    def test_renewable_energy_hits_simulated(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        result = web_search("renewable energy")
        assert len(result) > 20

    def test_unknown_query_returns_fallback_string(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        result = web_search("zzz_no_match_xyz")
        assert isinstance(result, str)

    def test_climate_policy_hits_simulated(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        result = web_search("climate policy")
        assert len(result) > 20


class TestCalculatorInFinalProject:
    def test_basic_addition(self):
        assert calculator("1 + 1") == "Result: 2"

    def test_sqrt(self):
        assert calculator("sqrt(4)") == "Result: 2.0"

    def test_error_on_invalid(self):
        assert calculator("bad @@").startswith("Error")


class TestExecuteToolFinalProject:
    def test_web_search_dispatch(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        result = execute_tool("web_search", {"query": "carbon capture"})
        assert isinstance(result, str)

    def test_calculator_dispatch(self):
        result = execute_tool("calculator", {"expression": "7 * 6"})
        assert result == "Result: 42"

    def test_unknown_tool_returns_error(self):
        result = execute_tool("ghost_tool", {})
        assert "Unknown" in result


class TestBuildSystemPrompt:
    def test_returns_list(self):
        result = build_system_prompt([])
        assert isinstance(result, list)

    def test_list_has_two_blocks(self):
        result = build_system_prompt([])
        assert len(result) == 2

    def test_first_block_has_cache_control(self):
        result = build_system_prompt([])
        first = result[0]
        assert "cache_control" in first
        assert first["cache_control"]["type"] == "ephemeral"

    def test_second_block_has_no_cache_control(self):
        result = build_system_prompt([])
        second = result[1]
        assert "cache_control" not in second

    def test_each_block_has_type_and_text(self):
        result = build_system_prompt([])
        for block in result:
            assert block.get("type") == "text"
            assert isinstance(block.get("text"), str)

    def test_with_chunks_includes_chunk_content(self):
        chunks = [{"content": "DAC costs $300-600/tonne", "source": "IEA.pdf", "page": 47, "distance": 0.3}]
        result = build_system_prompt(chunks)
        combined = " ".join(b["text"] for b in result)
        assert "DAC" in combined or "300" in combined

    def test_without_chunks_says_no_relevant(self):
        result = build_system_prompt([])
        combined = " ".join(b["text"] for b in result)
        assert "No relevant" in combined or "not found" in combined.lower()

    def test_stable_block_contains_identity(self):
        result = build_system_prompt([])
        assert "Research Assistant" in result[0]["text"] or "climate" in result[0]["text"].lower()


class TestResearchDocuments:
    def test_is_list(self):
        assert isinstance(RESEARCH_DOCUMENTS, list)

    def test_has_multiple_documents(self):
        assert len(RESEARCH_DOCUMENTS) >= 3

    def test_each_doc_has_required_keys(self):
        for doc in RESEARCH_DOCUMENTS:
            assert "id"      in doc
            assert "source"  in doc
            assert "page"    in doc
            assert "content" in doc

    def test_all_ids_unique(self):
        ids = [d["id"] for d in RESEARCH_DOCUMENTS]
        assert len(ids) == len(set(ids))

    def test_content_is_non_empty(self):
        for doc in RESEARCH_DOCUMENTS:
            assert len(doc["content"]) > 20


class TestFinalProjectTools:
    def test_tools_is_list(self):
        assert isinstance(TOOLS, list)

    def test_has_web_search_tool(self):
        names = [t["name"] for t in TOOLS]
        assert "web_search" in names

    def test_has_calculator_tool(self):
        names = [t["name"] for t in TOOLS]
        assert "calculator" in names

    def test_keyword_check_matches_expected(self):
        assert keyword_check("costs range from $300-600 per tonne", ["300", "600", "tonne"])

    def test_keyword_check_fallback(self):
        assert keyword_check("I don't have that information", ["don't have", "not found"])
