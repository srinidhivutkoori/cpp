"""
Reviewer management module for academic conference paper reviews.
"""

import random
from datetime import datetime


class ReviewManager:
    """Handles reviewer assignment, review validation, and review statistics."""

    def assign_reviewers(self, paper, reviewers, count=3):
        """
        Randomly select reviewers for a paper, avoiding conflicts of interest.

        A conflict exists when a reviewer is also an author of the paper.

        Args:
            paper (dict): Paper data containing an 'authors' list.
            reviewers (list[str]): Pool of available reviewer names.
            count (int): Number of reviewers to assign (default 3).

        Returns:
            list[str]: Selected reviewer names, or fewer if not enough eligible.
        """
        paper_authors = set(paper.get("authors", []))
        eligible = [r for r in reviewers if r not in paper_authors]

        if len(eligible) <= count:
            return eligible

        return random.sample(eligible, count)

    def validate_review(self, data):
        """
        Validate review submission data.

        Args:
            data (dict): Review data with score, comments, recommendation.

        Returns:
            tuple: (is_valid: bool, errors: list[str])
        """
        errors = []

        # Score validation
        score = data.get("score")
        if score is None:
            errors.append("Score is required.")
        elif not isinstance(score, (int, float)) or score < 1 or score > 10:
            errors.append("Score must be a number between 1 and 10.")

        # Comments validation
        comments = data.get("comments", "")
        if not comments or not isinstance(comments, str):
            errors.append("Comments are required and must be a string.")
        elif len(comments) < 50:
            errors.append("Comments must be at least 50 characters.")

        # Recommendation validation
        valid_recommendations = ["accept", "reject", "revision"]
        recommendation = data.get("recommendation", "")
        if recommendation not in valid_recommendations:
            errors.append(
                f"Recommendation must be one of: {', '.join(valid_recommendations)}."
            )

        return (len(errors) == 0, errors)

    def calculate_acceptance_rate(self, papers):
        """
        Calculate the percentage of accepted papers.

        Args:
            papers (list[dict]): Papers, each with a 'status' key.

        Returns:
            float: Acceptance rate as a percentage (0-100), rounded to 2 decimals.
        """
        if not papers:
            return 0.0
        accepted = sum(1 for p in papers if p.get("status") == "accepted")
        return round((accepted / len(papers)) * 100, 2)

    def get_review_stats(self, reviews):
        """
        Compute aggregate statistics for a set of reviews.

        Args:
            reviews (list[dict]): Each dict should have 'score' and 'recommendation'.

        Returns:
            dict: Keys — avg_score, min_score, max_score, count,
                  recommendation_breakdown (dict of recommendation -> count).
        """
        if not reviews:
            return {
                "avg_score": 0.0,
                "min_score": 0,
                "max_score": 0,
                "count": 0,
                "recommendation_breakdown": {},
            }

        scores = [r["score"] for r in reviews]
        breakdown = {}
        for r in reviews:
            rec = r.get("recommendation", "unknown")
            breakdown[rec] = breakdown.get(rec, 0) + 1

        return {
            "avg_score": round(sum(scores) / len(scores), 2),
            "min_score": min(scores),
            "max_score": max(scores),
            "count": len(reviews),
            "recommendation_breakdown": breakdown,
        }

    def check_review_deadline(self, review, deadline_str):
        """
        Check whether a review is overdue based on a deadline string.

        Args:
            review (dict): Review data (unused beyond presence check).
            deadline_str (str): Deadline in ISO format (YYYY-MM-DD).

        Returns:
            bool: True if the current date is past the deadline (overdue).
        """
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        return datetime.now() > deadline
