"""
Unit tests for the Reviewer class.
Tests expertise matching, conflict detection, and assignment optimization.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from paperflow.reviewer import Reviewer


class TestExpertiseMatching:
    """Tests for reviewer expertise matching algorithms."""

    def test_exact_match(self):
        """Test perfect expertise match with identical keywords."""
        reviewer = Reviewer("Dr. Smith", "smith@uni.edu",
                           expertise_areas=["machine learning", "cloud computing"])
        score = reviewer.calculate_expertise_match(["machine learning", "cloud computing"])
        assert score > 0.8

    def test_no_match(self):
        """Test zero match with completely different expertise."""
        reviewer = Reviewer("Dr. Smith", "smith@uni.edu",
                           expertise_areas=["biology", "chemistry"])
        score = reviewer.calculate_expertise_match(["machine learning", "cloud computing"])
        assert score == 0.0

    def test_partial_match(self):
        """Test partial match with some overlapping keywords."""
        reviewer = Reviewer("Dr. Smith", "smith@uni.edu",
                           expertise_areas=["machine learning", "NLP", "statistics"])
        score = reviewer.calculate_expertise_match(["machine learning", "cloud computing"])
        assert 0.0 < score < 1.0

    def test_empty_expertise(self):
        """Test match with no expertise areas defined."""
        reviewer = Reviewer("Dr. Smith", "smith@uni.edu", expertise_areas=[])
        score = reviewer.calculate_expertise_match(["AI"])
        assert score == 0.0

    def test_empty_keywords(self):
        """Test match with no paper keywords."""
        reviewer = Reviewer("Dr. Smith", "smith@uni.edu", expertise_areas=["AI"])
        score = reviewer.calculate_expertise_match([])
        assert score == 0.0


class TestConflictDetection:
    """Tests for conflict of interest detection."""

    def test_affiliation_conflict(self):
        """Test detection of same-affiliation conflict."""
        reviewer = Reviewer("Dr. Smith", "smith@nci.ie",
                           expertise_areas=["AI"], affiliation="NCI")
        result = reviewer.detect_conflict_of_interest(
            ["John Doe"], paper_affiliation="NCI"
        )
        assert result['has_conflict'] is True

    def test_no_conflict(self):
        """Test that different affiliations produce no conflict."""
        reviewer = Reviewer("Dr. Smith", "smith@mit.edu",
                           expertise_areas=["AI"], affiliation="MIT")
        result = reviewer.detect_conflict_of_interest(
            ["John Doe"], paper_affiliation="Stanford"
        )
        assert result['has_conflict'] is False

    def test_name_conflict(self):
        """Test detection of same-last-name conflict."""
        reviewer = Reviewer("Dr. Jane Smith", "jane@uni.edu",
                           expertise_areas=["AI"], affiliation="MIT")
        result = reviewer.detect_conflict_of_interest(
            ["John Smith"], paper_affiliation="Stanford"
        )
        assert result['has_conflict'] is True


class TestAssignment:
    """Tests for reviewer assignment management."""

    def test_assign_paper(self):
        """Test successful paper assignment."""
        reviewer = Reviewer("Dr. Smith", "smith@uni.edu", max_reviews=3)
        assert reviewer.assign_paper(1) is True
        assert 1 in reviewer.current_assignments

    def test_assign_at_capacity(self):
        """Test that assignment fails when at maximum capacity."""
        reviewer = Reviewer("Dr. Smith", "smith@uni.edu", max_reviews=1)
        reviewer.assign_paper(1)
        assert reviewer.assign_paper(2) is False

    def test_complete_review(self):
        """Test completing a review moves it to completed list."""
        reviewer = Reviewer("Dr. Smith", "smith@uni.edu", max_reviews=3)
        reviewer.assign_paper(1)
        assert reviewer.complete_review(1) is True
        assert 1 not in reviewer.current_assignments
        assert 1 in reviewer.completed_reviews

    def test_workload_score(self):
        """Test workload score calculation."""
        reviewer = Reviewer("Dr. Smith", "smith@uni.edu", max_reviews=4)
        reviewer.assign_paper(1)
        reviewer.assign_paper(2)
        assert reviewer.get_workload_score() == 0.5

    def test_optimize_assignments(self):
        """Test bulk reviewer-paper assignment optimization."""
        reviewers = [
            Reviewer("Dr. A", "a@uni.edu", expertise_areas=["AI", "ML"], affiliation="MIT"),
            Reviewer("Dr. B", "b@uni.edu", expertise_areas=["cloud", "security"], affiliation="Stanford"),
            Reviewer("Dr. C", "c@uni.edu", expertise_areas=["AI", "NLP"], affiliation="Oxford"),
        ]
        papers = [
            {'id': 1, 'keywords': ['AI', 'ML'], 'authors': ['John Doe'], 'affiliation': 'NCI'},
            {'id': 2, 'keywords': ['cloud', 'security'], 'authors': ['Jane Doe'], 'affiliation': 'NCI'},
        ]
        assignments = Reviewer.optimize_assignments(reviewers, papers)
        assert len(assignments) > 0
        # Verify assignments have required fields
        for a in assignments:
            assert 'paper_id' in a
            assert 'reviewer_name' in a
            assert 'match_score' in a

    def test_get_profile(self):
        """Test reviewer profile generation."""
        reviewer = Reviewer("Dr. Smith", "smith@uni.edu",
                           expertise_areas=["AI"], affiliation="MIT", max_reviews=5)
        profile = reviewer.get_profile()
        assert profile['name'] == "Dr. Smith"
        assert profile['available'] is True
