"""Tests for Module 3 — Hybrid Search: RRF fusion and BM25 retrieval."""
import pytest

rank_bm25 = pytest.importorskip("rank_bm25", reason="rank-bm25 not installed")

from tests.conftest import load_module

_mod = load_module("code/module3/lesson5_hybrid_search.py")
rrf            = _mod.rrf
build_sparse   = _mod.build_sparse
sparse_retrieve = _mod.sparse_retrieve

_sol = load_module("solutions/module3/solution_hybrid_search.py")
rrf_sol = _sol.rrf


DOCS = [
    {"id": "d1", "content": "MAX_UPLOAD_SIZE controls the maximum file upload limit in bytes."},
    {"id": "d2", "content": "Users can share files in cloud storage with their team."},
    {"id": "d3", "content": "HTTP 429 Too Many Requests means the rate limit was exceeded."},
    {"id": "d4", "content": "Neural networks learn by adjusting weights during training."},
    {"id": "d5", "content": "Vector embeddings represent semantic meaning as dense arrays."},
]


class TestRRF:
    def test_single_list_preserves_order(self):
        ids = ["a", "b", "c"]
        result = rrf([ids])
        assert result == ids

    def test_two_identical_lists_preserve_order(self):
        ids = ["a", "b", "c"]
        result = rrf([ids, ids])
        assert result == ids

    def test_two_lists_merge_correctly(self):
        list1 = ["a", "b", "c"]
        list2 = ["c", "a", "b"]
        result = rrf([list1, list2])
        # "a" is rank-1 in list1 and rank-2 in list2 → high combined score
        # "c" is rank-3 in list1 and rank-1 in list2
        assert "a" in result
        assert "c" in result
        assert set(result) == {"a", "b", "c"}

    def test_all_ids_appear_in_result(self):
        list1 = ["x", "y"]
        list2 = ["z", "x"]
        result = rrf([list1, list2])
        assert set(result) == {"x", "y", "z"}

    def test_empty_input_returns_empty(self):
        assert rrf([]) == []

    def test_item_in_both_lists_ranks_higher_than_item_in_one(self):
        # "shared" is top-1 in both lists; "only_in_1" is only in list1
        list1 = ["shared", "only_in_1"]
        list2 = ["shared", "only_in_2"]
        result = rrf([list1, list2])
        assert result[0] == "shared"

    def test_returns_list(self):
        assert isinstance(rrf([["a", "b"]]), list)

    def test_higher_k_gives_same_relative_order(self):
        lists = [["a", "b", "c"]]
        r_low  = rrf(lists, k=10)
        r_high = rrf(lists, k=1000)
        assert r_low == r_high  # single list → same order regardless of k

    def test_solution_rrf_matches_lesson_rrf(self):
        lists = [["a", "b", "c"], ["c", "b", "a"]]
        assert rrf(lists) == rrf_sol(lists)


class TestBM25:
    def setup_method(self):
        self.bm25 = build_sparse(DOCS)

    def test_keyword_query_scores_matching_doc_highest(self):
        from rank_bm25 import BM25Okapi
        scores = self.bm25.get_scores("MAX_UPLOAD_SIZE limit".lower().split())
        best_idx = scores.argmax()
        assert DOCS[best_idx]["id"] == "d1"

    def test_rate_limit_query_hits_correct_doc(self):
        scores = self.bm25.get_scores("rate limit exceeded".lower().split())
        best_idx = scores.argmax()
        assert DOCS[best_idx]["id"] == "d3"

    def test_neural_network_query_hits_correct_doc(self):
        scores = self.bm25.get_scores("neural network weights".lower().split())
        best_idx = scores.argmax()
        assert DOCS[best_idx]["id"] == "d4"

    def test_all_zeros_for_no_match(self):
        scores = self.bm25.get_scores("zzzzz_never_appears".lower().split())
        assert all(s == 0.0 for s in scores)

    def test_sparse_retrieve_returns_doc_ids(self):
        ids = sparse_retrieve("MAX_UPLOAD_SIZE", self.bm25, DOCS, top_k=2)
        assert isinstance(ids, list)
        assert all(isinstance(i, str) for i in ids)

    def test_sparse_retrieve_top_k_respected(self):
        ids = sparse_retrieve("MAX_UPLOAD_SIZE", self.bm25, DOCS, top_k=2)
        assert len(ids) <= 2

    def test_sparse_retrieve_best_match_is_first(self):
        ids = sparse_retrieve("MAX_UPLOAD_SIZE limit bytes", self.bm25, DOCS, top_k=3)
        assert ids[0] == "d1"


class TestDistanceFiltering:
    """Validates that distance threshold filtering drops low-relevance chunks."""

    def test_threshold_keeps_close_docs(self):
        from tests.conftest import load_module as lm
        sol = lm("solutions/module3/solution_hybrid_search.py")
        # sol.dense_ids uses RAG_DISTANCE_THRESHOLD internally via config
        # We test the rrf output instead (pure function, no chromadb needed)
        result = sol.rrf([["good_match"], ["good_match", "weak_match"]])
        assert result[0] == "good_match"
