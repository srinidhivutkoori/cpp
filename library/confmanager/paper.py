"""
Paper management module for academic conference submissions.
"""

import random
import string
from datetime import datetime


class PaperManager:
    """Handles paper creation, validation, status tracking, and citation formatting."""

    # Valid status transitions: current_status -> list of allowed next statuses
    STATUS_TRANSITIONS = {
        "submitted": ["under_review"],
        "under_review": ["accepted", "rejected", "revision_required"],
        "revision_required": ["resubmitted"],
        "resubmitted": ["under_review"],
    }

    def generate_paper_id(self, conference_code):
        """
        Generate a unique paper ID.

        Args:
            conference_code (str): Short code for the conference (e.g. 'ICSE').

        Returns:
            str: Paper ID in format PAPER-{CONF}-{YYYYMMDD}-{random4}.
        """
        date_str = datetime.now().strftime("%Y%m%d")
        rand_part = "".join(random.choices(string.digits, k=4))
        return f"PAPER-{conference_code.upper()}-{date_str}-{rand_part}"

    def validate_paper(self, data):
        """
        Validate paper submission data.

        Args:
            data (dict): Paper data with keys title, abstract, authors, keywords.

        Returns:
            tuple: (is_valid: bool, errors: list[str])
        """
        errors = []

        # Title validation
        title = data.get("title", "")
        if not title or not isinstance(title, str):
            errors.append("Title is required and must be a string.")
        elif len(title) < 10 or len(title) > 300:
            errors.append("Title must be between 10 and 300 characters.")

        # Abstract validation
        abstract = data.get("abstract", "")
        if not abstract or not isinstance(abstract, str):
            errors.append("Abstract is required and must be a string.")
        elif len(abstract) < 50 or len(abstract) > 3000:
            errors.append("Abstract must be between 50 and 3000 characters.")

        # Authors validation
        authors = data.get("authors", [])
        if not isinstance(authors, list) or len(authors) < 1:
            errors.append("At least one author is required.")

        # Keywords validation
        keywords = data.get("keywords", [])
        if not isinstance(keywords, list) or len(keywords) < 1:
            errors.append("At least one keyword is required.")

        return (len(errors) == 0, errors)

    def get_paper_status_flow(self):
        """
        Return the valid status transitions for paper workflow.

        Returns:
            dict: Mapping of current status to list of valid next statuses.
        """
        return dict(self.STATUS_TRANSITIONS)

    def validate_status_transition(self, current, new):
        """
        Check whether a status transition is valid.

        Args:
            current (str): Current paper status.
            new (str): Proposed new status.

        Returns:
            bool: True if the transition is allowed.
        """
        allowed = self.STATUS_TRANSITIONS.get(current, [])
        return new in allowed

    def calculate_review_score(self, reviews):
        """
        Calculate the average review score from a list of reviews.

        Args:
            reviews (list[dict]): Each dict must have a 'score' key (1-10).

        Returns:
            float: Average score rounded to 2 decimal places, or 0.0 if empty.
        """
        if not reviews:
            return 0.0
        total = sum(r["score"] for r in reviews)
        return round(total / len(reviews), 2)

    def format_citation(self, paper, style="ieee"):
        """
        Format a paper citation in the given style.

        Args:
            paper (dict): Paper data with title, authors, year, conference, pages.
            style (str): Citation style — currently supports 'ieee' and 'apa'.

        Returns:
            str: Formatted citation string.
        """
        authors = paper.get("authors", [])
        title = paper.get("title", "")
        year = paper.get("year", datetime.now().year)
        conference = paper.get("conference", "")
        pages = paper.get("pages", "")

        if style == "apa":
            author_str = ", ".join(authors)
            citation = f"{author_str} ({year}). {title}. {conference}"
            if pages:
                citation += f", pp. {pages}"
            citation += "."
        else:
            # IEEE style (default)
            author_str = ", ".join(authors)
            citation = f'{author_str}, "{title}," in {conference}, {year}'
            if pages:
                citation += f", pp. {pages}"
            citation += "."
        return citation
