"""
Unit tests for the Scoring class.
Tests weighted aggregation, statistical analysis, and recommendation generation.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from paperflow.scoring import Scoring


@pytest.fixture
def sample_reviews():
    """Create a set of sample reviews for testing."""
    return [
        {
            'originality_score': 8, 'significance_score': 7,
            'clarity_score': 9, 'methodology_score': 8,
            'overall_score': 8, 'recommendation': 'accept'
        },
        {
            'originality_score': 7, 'significance_score': 8,
            'clarity_score': 7, 'methodology_score': 7,
            'overall_score': 7, 'recommendation': 'accept'
        },
        {
            'originality_score': 6, 'significance_score': 6,
            'clarity_score': 8, 'methodology_score': 6,
            'overall_score': 6, 'recommendation': 'weak_accept'
        }
    ]


class TestWeightedScoring:
    """Tests for weighted score calculation."""

    def test_calculate_weighted_score(self, sample_reviews):
        """Test weighted score calculation for a single review."""
        scoring = Scoring()
        score = scoring.calculate_weighted_score(sample_reviews[0])
        assert 7.0 <= score <= 9.0

    def test_aggregate_score(self, sample_reviews):
        """Test aggregate score across multiple reviews."""
        scoring = Scoring(reviews=sample_reviews)
        aggregate = scoring.calculate_aggregate_score()
        assert 6.0 <= aggregate <= 9.0

    def test_aggregate_empty(self):
        """Test aggregate score with no reviews."""
        scoring = Scoring()
        assert scoring.calculate_aggregate_score() == 0.0

    def test_custom_weights(self, sample_reviews):
        """Test scoring with custom dimension weights."""
        custom_weights = {
            'originality': 0.40, 'significance': 0.30,
            'clarity': 0.10, 'methodology': 0.10, 'overall': 0.10
        }
        scoring = Scoring(reviews=sample_reviews, weights=custom_weights)
        score = scoring.calculate_aggregate_score()
        assert score > 0

    def test_add_review(self):
        """Test adding a review to the scoring pool."""
        scoring = Scoring()
        scoring.add_review({'overall_score': 8})
        assert len(scoring.reviews) == 1


class TestStatisticalAnalysis:
    """Tests for statistical analysis of review scores."""

    def test_calculate_mean(self, sample_reviews):
        """Test mean calculation for a dimension."""
        scoring = Scoring(reviews=sample_reviews)
        mean = scoring.calculate_mean('overall_score')
        assert mean == 7.0

    def test_calculate_median(self, sample_reviews):
        """Test median calculation for a dimension."""
        scoring = Scoring(reviews=sample_reviews)
        median = scoring.calculate_median('overall_score')
        assert median == 7.0

    def test_calculate_std_deviation(self, sample_reviews):
        """Test standard deviation calculation."""
        scoring = Scoring(reviews=sample_reviews)
        std = scoring.calculate_std_deviation('overall_score')
        assert std >= 0
        assert std <= 5.0

    def test_std_deviation_single_review(self):
        """Test standard deviation with only one review."""
        scoring = Scoring(reviews=[{'overall_score': 8}])
        std = scoring.calculate_std_deviation('overall_score')
        assert std == 0.0

    def test_dimension_report(self, sample_reviews):
        """Test dimension-level statistical report."""
        scoring = Scoring(reviews=sample_reviews)
        report = scoring.get_dimension_report()
        assert 'overall_score' in report
        assert 'mean' in report['overall_score']
        assert 'median' in report['overall_score']
        assert 'std_deviation' in report['overall_score']

    def test_score_distribution(self, sample_reviews):
        """Test score distribution calculation."""
        scoring = Scoring(reviews=sample_reviews)
        dist = scoring.get_score_distribution('overall_score')
        assert isinstance(dist, dict)
        assert sum(dist.values()) == 3


class TestRecommendation:
    """Tests for recommendation generation."""

    def test_accept_recommendation(self):
        """Test that high scores produce accept recommendation."""
        reviews = [
            {'originality_score': 9, 'significance_score': 8,
             'clarity_score': 9, 'methodology_score': 8,
             'overall_score': 9, 'recommendation': 'accept'},
            {'originality_score': 8, 'significance_score': 9,
             'clarity_score': 8, 'methodology_score': 9,
             'overall_score': 8, 'recommendation': 'accept'}
        ]
        scoring = Scoring(reviews=reviews)
        rec = scoring.generate_recommendation()
        assert rec['decision'] in ('accept', 'strong_accept')

    def test_reject_recommendation(self):
        """Test that low scores produce reject recommendation."""
        reviews = [
            {'originality_score': 2, 'significance_score': 3,
             'clarity_score': 2, 'methodology_score': 3,
             'overall_score': 2, 'recommendation': 'reject'},
            {'originality_score': 3, 'significance_score': 2,
             'clarity_score': 3, 'methodology_score': 2,
             'overall_score': 3, 'recommendation': 'reject'}
        ]
        scoring = Scoring(reviews=reviews)
        rec = scoring.generate_recommendation()
        assert rec['decision'] in ('reject', 'weak_reject')

    def test_empty_recommendation(self):
        """Test recommendation with no reviews."""
        scoring = Scoring()
        rec = scoring.generate_recommendation()
        assert rec['decision'] == 'pending'

    def test_disagreement_detection(self, sample_reviews):
        """Test reviewer disagreement detection."""
        scoring = Scoring(reviews=sample_reviews)
        result = scoring.detect_reviewer_disagreement(threshold=3.0)
        assert 'has_disagreement' in result
        assert 'score_range' in result

    def test_high_disagreement(self):
        """Test detection of significant reviewer disagreement."""
        reviews = [
            {'overall_score': 9, 'recommendation': 'strong_accept'},
            {'overall_score': 3, 'recommendation': 'reject'}
        ]
        scoring = Scoring(reviews=reviews)
        result = scoring.detect_reviewer_disagreement(threshold=3.0)
        assert result['has_disagreement'] is True

    def test_set_threshold(self):
        """Test updating the acceptance threshold."""
        scoring = Scoring()
        scoring.set_acceptance_threshold(7.5)
        assert scoring.acceptance_threshold == 7.5
