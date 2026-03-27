"""Tests for the PaperFormatter class."""

from confmanager.formatter import PaperFormatter


class TestPaperFormatter:
    """Test suite for PaperFormatter."""

    def setup_method(self):
        self.pf = PaperFormatter()

    def test_format_paper_summary(self):
        paper = {"title": "Test Paper", "authors": ["Alice"], "status": "submitted"}
        summary = self.pf.format_paper_summary(paper)
        assert "[SUBMITTED]" in summary
        assert "Test Paper" in summary

    def test_format_paper_detail_without_reviews(self):
        paper = {
            "title": "Test Paper",
            "authors": ["Alice"],
            "status": "submitted",
            "keywords": ["AI"],
            "abstract": "An abstract.",
        }
        detail = self.pf.format_paper_detail(paper)
        assert "Test Paper" in detail
        assert "Alice" in detail

    def test_format_paper_detail_with_reviews(self):
        paper = {
            "title": "Test Paper",
            "authors": ["Alice"],
            "status": "under_review",
            "keywords": ["AI"],
            "abstract": "An abstract.",
        }
        reviews = [{"score": 8, "recommendation": "accept", "comments": "Good work"}]
        detail = self.pf.format_paper_detail(paper, reviews)
        assert "Reviews (1)" in detail
        assert "8/10" in detail

    def test_to_csv(self):
        papers = [
            {
                "title": "Paper A",
                "authors": ["Alice"],
                "status": "accepted",
                "score": 8,
                "keywords": ["ML"],
                "submitted_date": "2026-01-01",
            }
        ]
        csv_str = self.pf.to_csv(papers)
        assert "Paper A" in csv_str
        assert "title,authors,status" in csv_str

    def test_format_acceptance_letter(self):
        paper = {"title": "Great Paper", "authors": ["Alice"]}
        conf = {"name": "ICSE 2026", "startDate": "2026-06-01", "endDate": "2026-06-05"}
        letter = self.pf.format_acceptance_letter(paper, conf)
        assert "ACCEPTED" in letter
        assert "ICSE 2026" in letter

    def test_format_rejection_letter(self):
        paper = {"title": "Paper B", "authors": ["Bob"], "reviews": []}
        conf = {"name": "ICSE 2026"}
        letter = self.pf.format_rejection_letter(paper, conf)
        assert "not been accepted" in letter

    def test_format_rejection_letter_with_reviews(self):
        paper = {
            "title": "Paper B",
            "authors": ["Bob"],
            "reviews": [{"score": 3, "comments": "Needs more work"}],
        }
        conf = {"name": "ICSE 2026"}
        letter = self.pf.format_rejection_letter(paper, conf)
        assert "Reviewer 1" in letter
