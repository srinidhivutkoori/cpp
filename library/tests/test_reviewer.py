"""Tests for the ReviewManager class."""

from confmanager.reviewer import ReviewManager


class TestReviewManager:
    """Test suite for ReviewManager."""

    def setup_method(self):
        self.rm = ReviewManager()

    def test_assign_reviewers_excludes_authors(self):
        paper = {"authors": ["Alice"]}
        reviewers = ["Alice", "Bob", "Carol", "Dave"]
        assigned = self.rm.assign_reviewers(paper, reviewers, count=2)
        assert "Alice" not in assigned
        assert len(assigned) == 2

    def test_assign_reviewers_fewer_eligible(self):
        paper = {"authors": ["Alice", "Bob"]}
        reviewers = ["Alice", "Bob", "Carol"]
        assigned = self.rm.assign_reviewers(paper, reviewers, count=3)
        assert assigned == ["Carol"]

    def test_validate_review_valid(self):
        data = {
            "score": 7,
            "comments": "A" * 60,
            "recommendation": "accept",
        }
        is_valid, errors = self.rm.validate_review(data)
        assert is_valid is True
        assert errors == []

    def test_validate_review_missing_score(self):
        data = {"comments": "A" * 60, "recommendation": "accept"}
        is_valid, errors = self.rm.validate_review(data)
        assert is_valid is False

    def test_validate_review_invalid_recommendation(self):
        data = {"score": 7, "comments": "A" * 60, "recommendation": "maybe"}
        is_valid, errors = self.rm.validate_review(data)
        assert is_valid is False

    def test_validate_review_short_comments(self):
        data = {"score": 7, "comments": "Short", "recommendation": "accept"}
        is_valid, errors = self.rm.validate_review(data)
        assert is_valid is False

    def test_calculate_acceptance_rate(self):
        papers = [
            {"status": "accepted"},
            {"status": "rejected"},
            {"status": "accepted"},
            {"status": "rejected"},
        ]
        assert self.rm.calculate_acceptance_rate(papers) == 50.0

    def test_calculate_acceptance_rate_empty(self):
        assert self.rm.calculate_acceptance_rate([]) == 0.0

    def test_get_review_stats(self):
        reviews = [
            {"score": 8, "recommendation": "accept"},
            {"score": 6, "recommendation": "revision"},
            {"score": 4, "recommendation": "reject"},
        ]
        stats = self.rm.get_review_stats(reviews)
        assert stats["count"] == 3
        assert stats["min_score"] == 4
        assert stats["max_score"] == 8
        assert stats["avg_score"] == 6.0

    def test_get_review_stats_empty(self):
        stats = self.rm.get_review_stats([])
        assert stats["count"] == 0
        assert stats["avg_score"] == 0.0
