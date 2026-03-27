"""
Scoring class for weighted review aggregation, statistical analysis,
and acceptance threshold calculation. Provides decision support for
conference program committees.
"""

import math
from datetime import datetime


class Scoring:
    """
    Aggregates and analyzes review scores to support paper acceptance decisions.

    Supports multiple scoring dimensions with configurable weights,
    statistical analysis, and threshold-based recommendations.

    Attributes:
        reviews (list): List of review score dictionaries.
        weights (dict): Weights for each scoring dimension.
        acceptance_threshold (float): Minimum score for acceptance.
    """

    # Default weights for scoring dimensions
    DEFAULT_WEIGHTS = {
        'originality': 0.25,
        'significance': 0.25,
        'clarity': 0.20,
        'methodology': 0.20,
        'overall': 0.10
    }

    # Default acceptance threshold (on a 1-10 scale)
    DEFAULT_THRESHOLD = 6.0

    def __init__(self, reviews=None, weights=None, acceptance_threshold=None):
        """
        Initialize a Scoring instance.

        Args:
            reviews (list): List of review dicts with score fields.
            weights (dict): Custom weights for scoring dimensions.
            acceptance_threshold (float): Custom acceptance threshold.
        """
        self.reviews = reviews or []
        self.weights = weights or self.DEFAULT_WEIGHTS.copy()
        self.acceptance_threshold = acceptance_threshold or self.DEFAULT_THRESHOLD

    def add_review(self, review):
        """
        Add a review to the scoring pool.

        Args:
            review (dict): Review data with score fields.
        """
        self.reviews.append(review)

    def calculate_weighted_score(self, review):
        """
        Calculate the weighted aggregate score for a single review.

        Args:
            review (dict): Review data with score fields.

        Returns:
            float: Weighted score between 0 and 10.
        """
        total = 0.0
        weight_sum = 0.0

        dimension_keys = {
            'originality': 'originality_score',
            'significance': 'significance_score',
            'clarity': 'clarity_score',
            'methodology': 'methodology_score',
            'overall': 'overall_score'
        }

        for dim, key in dimension_keys.items():
            score = review.get(key)
            weight = self.weights.get(dim, 0)
            if score is not None:
                total += score * weight
                weight_sum += weight

        if weight_sum == 0:
            return 0.0
        return round(total / weight_sum, 3)

    def calculate_aggregate_score(self):
        """
        Calculate the aggregate weighted score across all reviews.

        Returns:
            float: Average weighted score across all reviews.
        """
        if not self.reviews:
            return 0.0

        scores = [self.calculate_weighted_score(r) for r in self.reviews]
        return round(sum(scores) / len(scores), 3)

    def calculate_mean(self, dimension):
        """
        Calculate the mean score for a specific dimension.

        Args:
            dimension (str): Score dimension key (e.g., 'originality_score').

        Returns:
            float: Mean score for the dimension.
        """
        values = [r.get(dimension, 0) for r in self.reviews if r.get(dimension) is not None]
        if not values:
            return 0.0
        return round(sum(values) / len(values), 3)

    def calculate_std_deviation(self, dimension):
        """
        Calculate the standard deviation for a specific dimension.
        Measures agreement or disagreement among reviewers.

        Args:
            dimension (str): Score dimension key.

        Returns:
            float: Standard deviation of scores.
        """
        values = [r.get(dimension, 0) for r in self.reviews if r.get(dimension) is not None]
        if len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return round(math.sqrt(variance), 3)

    def calculate_median(self, dimension):
        """
        Calculate the median score for a specific dimension.

        Args:
            dimension (str): Score dimension key.

        Returns:
            float: Median score.
        """
        values = sorted(
            [r.get(dimension, 0) for r in self.reviews if r.get(dimension) is not None]
        )
        if not values:
            return 0.0

        n = len(values)
        if n % 2 == 0:
            return round((values[n // 2 - 1] + values[n // 2]) / 2, 3)
        return float(values[n // 2])

    def detect_reviewer_disagreement(self, threshold=3.0):
        """
        Detect significant disagreement among reviewers.
        A high standard deviation in overall scores indicates disagreement.

        Args:
            threshold (float): Score difference threshold for flagging.

        Returns:
            dict: Disagreement analysis result.
        """
        overall_scores = [
            r.get('overall_score', 0)
            for r in self.reviews if r.get('overall_score') is not None
        ]

        if len(overall_scores) < 2:
            return {
                'has_disagreement': False,
                'message': 'Insufficient reviews for disagreement analysis.'
            }

        score_range = max(overall_scores) - min(overall_scores)
        std_dev = self.calculate_std_deviation('overall_score')

        has_disagreement = score_range >= threshold

        return {
            'has_disagreement': has_disagreement,
            'score_range': score_range,
            'std_deviation': std_dev,
            'min_score': min(overall_scores),
            'max_score': max(overall_scores),
            'reviewer_count': len(overall_scores),
            'needs_additional_review': has_disagreement
        }

    def generate_recommendation(self):
        """
        Generate an acceptance recommendation based on aggregated scores.

        Returns:
            dict: Recommendation with decision and confidence level.
        """
        if not self.reviews:
            return {
                'decision': 'pending',
                'confidence': 'none',
                'reason': 'No reviews available.'
            }

        aggregate = self.calculate_aggregate_score()
        disagreement = self.detect_reviewer_disagreement()

        if aggregate >= self.acceptance_threshold + 2:
            decision = 'strong_accept'
            confidence = 'high'
        elif aggregate >= self.acceptance_threshold:
            decision = 'accept'
            confidence = 'medium' if disagreement['has_disagreement'] else 'high'
        elif aggregate >= self.acceptance_threshold - 1:
            decision = 'borderline'
            confidence = 'low'
        elif aggregate >= self.acceptance_threshold - 2:
            decision = 'weak_reject'
            confidence = 'medium'
        else:
            decision = 'reject'
            confidence = 'high' if not disagreement['has_disagreement'] else 'medium'

        # Recommendation counts from reviewers
        rec_counts = {}
        for r in self.reviews:
            rec = r.get('recommendation', 'unknown')
            rec_counts[rec] = rec_counts.get(rec, 0) + 1

        return {
            'decision': decision,
            'confidence': confidence,
            'aggregate_score': aggregate,
            'threshold': self.acceptance_threshold,
            'review_count': len(self.reviews),
            'disagreement': disagreement,
            'recommendation_distribution': rec_counts,
            'generated_at': datetime.utcnow().isoformat()
        }

    def get_dimension_report(self):
        """
        Generate a statistical report for each scoring dimension.

        Returns:
            dict: Statistics for each dimension.
        """
        dimensions = [
            'originality_score', 'significance_score',
            'clarity_score', 'methodology_score', 'overall_score'
        ]

        report = {}
        for dim in dimensions:
            report[dim] = {
                'mean': self.calculate_mean(dim),
                'median': self.calculate_median(dim),
                'std_deviation': self.calculate_std_deviation(dim)
            }

        return report

    def get_score_distribution(self, dimension='overall_score'):
        """
        Get the distribution of scores for a given dimension.

        Args:
            dimension (str): Score dimension to analyze.

        Returns:
            dict: Score distribution with counts per value.
        """
        distribution = {}
        for r in self.reviews:
            score = r.get(dimension)
            if score is not None:
                distribution[score] = distribution.get(score, 0) + 1
        return dict(sorted(distribution.items()))

    def set_acceptance_threshold(self, threshold):
        """
        Update the acceptance threshold.

        Args:
            threshold (float): New threshold value.
        """
        self.acceptance_threshold = threshold

    def __repr__(self):
        return f'Scoring(reviews={len(self.reviews)}, threshold={self.acceptance_threshold})'
