"""Tests for Module 6 — security patterns, canary detection, keyword checking."""
import pytest
from tests.conftest import load_module

_sec = load_module("code/module6/lesson3_security.py")
build_hardened_system = _sec.build_hardened_system
ATTACK_TESTS          = _sec.ATTACK_TESTS

_eval = load_module("final_project/evaluate.py")
keyword_check = _eval.keyword_check


class TestKeywordCheck:
    def test_exact_match_returns_true(self):
        assert keyword_check("the answer is 42", ["42"]) is True

    def test_no_match_returns_false(self):
        assert keyword_check("hello world", ["42"]) is False

    def test_case_insensitive_match(self):
        assert keyword_check("The Sky Is Blue", ["blue"]) is True
        assert keyword_check("THE SKY IS BLUE", ["Blue"]) is True

    def test_partial_word_match(self):
        assert keyword_check("photosynthesis is important", ["photosyn"]) is True

    def test_multiple_keywords_one_matches(self):
        assert keyword_check("the ocean is vast", ["mountain", "ocean", "desert"]) is True

    def test_multiple_keywords_none_match(self):
        assert keyword_check("the ocean is vast", ["mountain", "desert"]) is False

    def test_empty_keywords_returns_false(self):
        assert keyword_check("anything", []) is False

    def test_empty_answer_returns_false(self):
        assert keyword_check("", ["keyword"]) is False

    def test_both_empty_returns_false(self):
        assert keyword_check("", []) is False

    def test_multi_word_keyword(self):
        assert keyword_check("direct air capture is promising", ["direct air"]) is True

    def test_keyword_at_start(self):
        assert keyword_check("photosynthesis converts CO2", ["photosyn"]) is True

    def test_keyword_at_end(self):
        assert keyword_check("the process is photosynthesis", ["photosyn"]) is True


class TestHardenedSystemPrompt:
    def test_returns_string(self):
        result = build_hardened_system("CANARY-TEST")
        assert isinstance(result, str)

    def test_contains_canary(self):
        canary = "CANARY-TESTTOKEN"
        result = build_hardened_system(canary)
        assert canary in result

    def test_contains_email_tag_instruction(self):
        result = build_hardened_system("CANARY-X")
        assert "<email>" in result or "email" in result.lower()

    def test_contains_never_reveal(self):
        result = build_hardened_system("CANARY-X")
        assert "NEVER" in result or "never" in result

    def test_different_canaries_produce_different_prompts(self):
        p1 = build_hardened_system("CANARY-AAA")
        p2 = build_hardened_system("CANARY-BBB")
        assert p1 != p2

    def test_prompt_is_non_trivial(self):
        result = build_hardened_system("CANARY-X")
        assert len(result) > 50


class TestAttackTestStructure:
    def test_attack_tests_is_list(self):
        assert isinstance(ATTACK_TESTS, list)

    def test_attack_tests_has_entries(self):
        assert len(ATTACK_TESTS) >= 3

    def test_each_entry_has_required_keys(self):
        for test in ATTACK_TESTS:
            assert "name"   in test, f"Missing 'name' in: {test}"
            assert "email"  in test, f"Missing 'email' in: {test}"
            assert "expect" in test, f"Missing 'expect' in: {test}"

    def test_expect_values_are_valid(self):
        valid = {"safe", "defended"}
        for test in ATTACK_TESTS:
            assert test["expect"] in valid, f"Invalid expect: {test['expect']}"

    def test_at_least_one_legitimate_email(self):
        assert any(t["expect"] == "safe" for t in ATTACK_TESTS)

    def test_at_least_one_attack(self):
        assert any(t["expect"] == "defended" for t in ATTACK_TESTS)

    def test_email_fields_are_strings(self):
        for test in ATTACK_TESTS:
            assert isinstance(test["email"], str)
            assert len(test["email"]) > 0
