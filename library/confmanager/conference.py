"""
Conference management module for academic conferences.
"""

from datetime import datetime


class ConferenceManager:
    """Handles conference validation, status checks, statistics, and reporting."""

    def validate_conference(self, data):
        """
        Validate conference data.

        Args:
            data (dict): Conference data with name, description, startDate,
                         endDate, submissionDeadline (all date strings as YYYY-MM-DD).

        Returns:
            tuple: (is_valid: bool, errors: list[str])
        """
        errors = []

        # Name validation
        name = data.get("name", "")
        if not name or not isinstance(name, str):
            errors.append("Conference name is required.")

        # Description validation
        description = data.get("description", "")
        if not description or not isinstance(description, str):
            errors.append("Conference description is required.")

        # Date validations
        start_str = data.get("startDate", "")
        end_str = data.get("endDate", "")
        start_date = None
        end_date = None

        if not start_str:
            errors.append("Start date is required.")
        else:
            try:
                start_date = datetime.strptime(start_str, "%Y-%m-%d")
            except ValueError:
                errors.append("Start date must be in YYYY-MM-DD format.")

        if not end_str:
            errors.append("End date is required.")
        else:
            try:
                end_date = datetime.strptime(end_str, "%Y-%m-%d")
            except ValueError:
                errors.append("End date must be in YYYY-MM-DD format.")

        if start_date and end_date and end_date <= start_date:
            errors.append("End date must be after start date.")

        # Submission deadline
        deadline_str = data.get("submissionDeadline", "")
        if not deadline_str:
            errors.append("Submission deadline is required.")
        else:
            try:
                datetime.strptime(deadline_str, "%Y-%m-%d")
            except ValueError:
                errors.append("Submission deadline must be in YYYY-MM-DD format.")

        return (len(errors) == 0, errors)

    def is_submission_open(self, conference):
        """
        Check whether submissions are still open for a conference.

        Args:
            conference (dict): Must contain 'submissionDeadline' in YYYY-MM-DD format.

        Returns:
            bool: True if current date is before the submission deadline.
        """
        deadline_str = conference.get("submissionDeadline", "")
        if not deadline_str:
            return False
        deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
        return datetime.now() < deadline

    def get_conference_stats(self, papers):
        """
        Compute submission statistics for a conference.

        Args:
            papers (list[dict]): Papers with 'status' key.

        Returns:
            dict: total, accepted, rejected, pending counts and acceptance_rate.
        """
        total = len(papers)
        accepted = sum(1 for p in papers if p.get("status") == "accepted")
        rejected = sum(1 for p in papers if p.get("status") == "rejected")
        pending = total - accepted - rejected
        rate = round((accepted / total) * 100, 2) if total > 0 else 0.0

        return {
            "total_submissions": total,
            "accepted": accepted,
            "rejected": rejected,
            "pending": pending,
            "acceptance_rate": rate,
        }

    def generate_conference_report(self, conference, papers):
        """
        Generate a formatted text report for a conference.

        Args:
            conference (dict): Conference data with name, startDate, endDate.
            papers (list[dict]): Papers submitted to the conference.

        Returns:
            str: Multi-line formatted report.
        """
        stats = self.get_conference_stats(papers)
        name = conference.get("name", "Unknown Conference")
        start = conference.get("startDate", "N/A")
        end = conference.get("endDate", "N/A")

        lines = [
            "=" * 60,
            f"CONFERENCE REPORT: {name}",
            "=" * 60,
            f"Dates: {start} to {end}",
            f"Total Submissions: {stats['total_submissions']}",
            f"Accepted: {stats['accepted']}",
            f"Rejected: {stats['rejected']}",
            f"Pending: {stats['pending']}",
            f"Acceptance Rate: {stats['acceptance_rate']}%",
            "=" * 60,
        ]
        return "\n".join(lines)

    def format_schedule(self, sessions):
        """
        Format a conference schedule from a list of session dicts.

        Args:
            sessions (list[dict]): Each session has 'time', 'title', 'speaker', 'room'.

        Returns:
            str: Formatted schedule text.
        """
        lines = [
            "CONFERENCE SCHEDULE",
            "-" * 50,
        ]
        for s in sessions:
            time = s.get("time", "TBD")
            title = s.get("title", "Untitled")
            speaker = s.get("speaker", "TBA")
            room = s.get("room", "TBD")
            lines.append(f"{time}  |  {title}")
            lines.append(f"          Speaker: {speaker}  |  Room: {room}")
            lines.append("-" * 50)
        return "\n".join(lines)
