"""
Unit tests for the Paper class.
Tests validation of title, abstract, keywords, file format, and metadata.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from paperflow.paper import Paper


class TestPaperValidation:
    """Tests for paper metadata validation."""

    def test_valid_title(self):
        """Test that a valid title passes validation."""
        paper = Paper("A Novel Approach to Cloud Computing", "x " * 100)
        valid, errors = paper.validate_title()
        assert valid is True
        assert len(errors) == 0

    def test_short_title(self):
        """Test that a too-short title fails validation."""
        paper = Paper("Short", "x " * 100)
        valid, errors = paper.validate_title()
        assert valid is False
        assert any('at least' in e for e in errors)

    def test_long_title(self):
        """Test that an excessively long title fails validation."""
        paper = Paper("A" * 301, "x " * 100)
        valid, errors = paper.validate_title()
        assert valid is False

    def test_lowercase_title_warning(self):
        """Test that a lowercase starting title gets flagged."""
        paper = Paper("a novel approach to computing", "x " * 100)
        valid, errors = paper.validate_title()
        assert valid is False
        assert any('capital' in e for e in errors)

    def test_valid_abstract(self):
        """Test that an abstract with valid word count passes."""
        abstract = " ".join(["word"] * 100)
        paper = Paper("Valid Title Here", abstract)
        valid, errors = paper.validate_abstract()
        assert valid is True

    def test_short_abstract(self):
        """Test that a too-short abstract fails validation."""
        paper = Paper("Valid Title Here", "Too short")
        valid, errors = paper.validate_abstract()
        assert valid is False
        assert any('at least' in e for e in errors)

    def test_long_abstract(self):
        """Test that an excessively long abstract fails validation."""
        abstract = " ".join(["word"] * 600)
        paper = Paper("Valid Title Here", abstract)
        valid, errors = paper.validate_abstract()
        assert valid is False

    def test_valid_keywords(self):
        """Test that a valid keyword list passes."""
        paper = Paper("Title", "x " * 100, keywords=["AI", "cloud", "NLP"])
        valid, errors = paper.validate_keywords()
        assert valid is True

    def test_too_few_keywords(self):
        """Test that too few keywords fail validation."""
        paper = Paper("Title", "x " * 100, keywords=["AI"])
        valid, errors = paper.validate_keywords()
        assert valid is False

    def test_duplicate_keywords(self):
        """Test that duplicate keywords are detected."""
        paper = Paper("Title", "x " * 100, keywords=["AI", "ai", "cloud"])
        valid, errors = paper.validate_keywords()
        assert valid is False
        assert any('unique' in e for e in errors)

    def test_valid_file_format(self):
        """Test that a PDF file passes format validation."""
        paper = Paper("Title", "x " * 100, file_name="paper.pdf")
        valid, errors = paper.validate_file_format()
        assert valid is True

    def test_invalid_file_format(self):
        """Test that a non-PDF file fails format validation."""
        paper = Paper("Title", "x " * 100, file_name="paper.docx")
        valid, errors = paper.validate_file_format()
        assert valid is False

    def test_no_file(self):
        """Test that missing file is caught."""
        paper = Paper("Title", "x " * 100)
        valid, errors = paper.validate_file_format()
        assert valid is False


class TestPaperMetrics:
    """Tests for paper metric calculations."""

    def test_word_count(self):
        """Test word count estimation."""
        abstract = "This is a test abstract with seven words."
        paper = Paper("Title", abstract)
        assert paper.estimate_word_count() == 8

    def test_word_count_empty(self):
        """Test word count with empty abstract."""
        paper = Paper("Title", "")
        assert paper.estimate_word_count() == 0

    def test_reading_time(self):
        """Test reading time estimation."""
        abstract = " ".join(["word"] * 200)
        paper = Paper("Title", abstract)
        assert paper.estimate_reading_time(200) == 1.0

    def test_extract_title_keywords(self):
        """Test keyword extraction from title."""
        paper = Paper("Machine Learning for Cloud Computing Optimization", "x " * 100)
        keywords = paper.extract_title_keywords()
        assert 'machine' in keywords
        assert 'learning' in keywords
        assert 'the' not in keywords

    def test_get_metadata(self):
        """Test metadata dictionary generation."""
        paper = Paper("Valid Title Here", "x " * 100, authors=["John Doe"],
                      keywords=["AI"], file_name="paper.pdf", page_count=10)
        meta = paper.get_metadata()
        assert meta['title'] == "Valid Title Here"
        assert meta['page_count'] == 10
        assert 'word_count' in meta

    def test_validate_all(self):
        """Test comprehensive validation."""
        paper = Paper(
            "A Valid Research Paper Title",
            " ".join(["word"] * 100),
            keywords=["AI", "cloud", "NLP"],
            file_name="paper.pdf"
        )
        report = paper.validate_all()
        assert report['is_valid'] is True
