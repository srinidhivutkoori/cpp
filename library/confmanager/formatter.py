"""
Paper formatting module for academic conference papers.
"""

import csv
import io


class PaperFormatter:
    """Handles paper display formatting, CSV export, and letter generation."""

    def format_paper_summary(self, paper):
        """
        Format a one-line summary of a paper.

        Args:
            paper (dict): Paper data with title, authors, status.

        Returns:
            str: One-line summary.
        """
        title = paper.get("title", "Untitled")
        authors = ", ".join(paper.get("authors", []))
        status = paper.get("status", "unknown")
        return f"[{status.upper()}] {title} — {authors}"

    def format_paper_detail(self, paper, reviews=None):
        """
        Format a detailed multi-line view of a paper with optional reviews.

        Args:
            paper (dict): Paper data with title, authors, abstract, keywords, status.
            reviews (list[dict], optional): Reviews with score, comments, recommendation.

        Returns:
            str: Multi-line detailed paper view.
        """
        lines = [
            "=" * 60,
            f"Title: {paper.get('title', 'Untitled')}",
            f"Authors: {', '.join(paper.get('authors', []))}",
            f"Status: {paper.get('status', 'unknown')}",
            f"Keywords: {', '.join(paper.get('keywords', []))}",
            "-" * 60,
            f"Abstract: {paper.get('abstract', 'N/A')}",
        ]

        if reviews:
            lines.append("-" * 60)
            lines.append(f"Reviews ({len(reviews)}):")
            for i, r in enumerate(reviews, 1):
                lines.append(f"  Review {i}:")
                lines.append(f"    Score: {r.get('score', 'N/A')}/10")
                lines.append(f"    Recommendation: {r.get('recommendation', 'N/A')}")
                lines.append(f"    Comments: {r.get('comments', 'N/A')}")

        lines.append("=" * 60)
        return "\n".join(lines)

    def to_csv(self, papers):
        """
        Convert a list of papers to CSV format.

        Columns: title, authors, status, score, keywords, submitted_date

        Args:
            papers (list[dict]): Paper data dicts.

        Returns:
            str: CSV-formatted string with header row.
        """
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["title", "authors", "status", "score", "keywords", "submitted_date"])

        for p in papers:
            writer.writerow([
                p.get("title", ""),
                "; ".join(p.get("authors", [])),
                p.get("status", ""),
                p.get("score", ""),
                "; ".join(p.get("keywords", [])),
                p.get("submitted_date", ""),
            ])

        return output.getvalue()

    def format_acceptance_letter(self, paper, conference):
        """
        Generate a formal acceptance letter.

        Args:
            paper (dict): Accepted paper data.
            conference (dict): Conference data with name, startDate, endDate.

        Returns:
            str: Formal acceptance letter text.
        """
        authors = ", ".join(paper.get("authors", []))
        title = paper.get("title", "Untitled")
        conf_name = conference.get("name", "the conference")
        start = conference.get("startDate", "TBD")
        end = conference.get("endDate", "TBD")

        return (
            f"Dear {authors},\n\n"
            f"We are pleased to inform you that your paper titled "
            f'"{title}" has been ACCEPTED for presentation at {conf_name}.\n\n'
            f"The conference will be held from {start} to {end}.\n\n"
            f"Please ensure that you submit the camera-ready version of your "
            f"paper by the deadline specified on the conference website.\n\n"
            f"We look forward to your participation.\n\n"
            f"Best regards,\n"
            f"{conf_name} Organising Committee"
        )

    def format_rejection_letter(self, paper, conference):
        """
        Generate a formal rejection letter with review feedback summary.

        Args:
            paper (dict): Rejected paper data, may include 'reviews'.
            conference (dict): Conference data with name.

        Returns:
            str: Formal rejection letter text.
        """
        authors = ", ".join(paper.get("authors", []))
        title = paper.get("title", "Untitled")
        conf_name = conference.get("name", "the conference")
        reviews = paper.get("reviews", [])

        letter = (
            f"Dear {authors},\n\n"
            f"Thank you for submitting your paper titled "
            f'"{title}" to {conf_name}.\n\n'
            f"After careful review, we regret to inform you that your paper "
            f"has not been accepted for this edition of the conference.\n\n"
        )

        if reviews:
            letter += "Reviewer feedback summary:\n"
            for i, r in enumerate(reviews, 1):
                letter += (
                    f"  Reviewer {i}: Score {r.get('score', 'N/A')}/10 "
                    f"— {r.get('comments', 'No comments provided.')}\n"
                )
            letter += "\n"

        letter += (
            "We encourage you to consider the feedback and resubmit to a "
            "future edition.\n\n"
            "Best regards,\n"
            f"{conf_name} Organising Committee"
        )
        return letter
