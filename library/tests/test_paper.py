"""Tests for the PaperManager class."""

from confmanager.paper import PaperManager


class TestPaperManager:
    """Test suite for PaperManager."""

    def setup_method(self):
        self.pm = PaperManager()

    def test_generate_paper_id_format(self):
        paper_id = self.pm.generate_paper_id("ICSE")
        assert paper_id.startswith("PAPER-ICSE-")
        parts = paper_id.split("-")
        assert len(parts) == 4

    def test_generate_paper_id_uppercase(self):
        paper_id = self.pm.generate_paper_id("icse")
        assert "ICSE" in paper_id

    def test_validate_paper_valid(self):
        data = {
            "title": "A Valid Paper Title for Testing",
            "abstract": "A" * 60,
            "authors": ["Author One"],
            "keywords": ["testing"],
        }
        is_valid, errors = self.pm.validate_paper(data)
        assert is_valid is True
        assert errors == []

    def test_validate_paper_missing_title(self):
        data = {"abstract": "A" * 60, "authors": ["Author"], "keywords": ["k"]}
        is_valid, errors = self.pm.validate_paper(data)
        assert is_valid is False
        assert any("Title" in e for e in errors)

    def test_validate_paper_short_abstract(self):
        data = {
            "title": "A Valid Paper Title for Testing",
            "abstract": "Short",
            "authors": ["Author"],
            "keywords": ["k"],
        }
        is_valid, errors = self.pm.validate_paper(data)
        assert is_valid is False
        assert any("Abstract" in e for e in errors)

    def test_validate_paper_no_authors(self):
        data = {
            "title": "A Valid Paper Title for Testing",
            "abstract": "A" * 60,
            "authors": [],
            "keywords": ["k"],
        }
        is_valid, errors = self.pm.validate_paper(data)
        assert is_valid is False

    def test_validate_status_transition_valid(self):
        assert self.pm.validate_status_transition("submitted", "under_review") is True

    def test_validate_status_transition_invalid(self):
        assert self.pm.validate_status_transition("submitted", "accepted") is False

    def test_calculate_review_score(self):
        reviews = [{"score": 8}, {"score": 6}, {"score": 7}]
        assert self.pm.calculate_review_score(reviews) == 7.0

    def test_calculate_review_score_empty(self):
        assert self.pm.calculate_review_score([]) == 0.0

    def test_format_citation_ieee(self):
        paper = {
            "authors": ["A. Smith"],
            "title": "Test Paper",
            "year": 2025,
            "conference": "ICSE 2025",
        }
        citation = self.pm.format_citation(paper, style="ieee")
        assert "ICSE 2025" in citation
        assert "Test Paper" in citation

    def test_format_citation_apa(self):
        paper = {
            "authors": ["A. Smith"],
            "title": "Test Paper",
            "year": 2025,
            "conference": "ICSE 2025",
        }
        citation = self.pm.format_citation(paper, style="apa")
        assert "(2025)" in citation

    def test_get_paper_status_flow(self):
        flow = self.pm.get_paper_status_flow()
        assert "submitted" in flow
        assert "under_review" in flow["submitted"]
