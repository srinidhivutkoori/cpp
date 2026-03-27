"""
Conference class for deadline management, track organization, and capacity planning.
Manages the lifecycle of an academic conference from setup to completion.
"""

from datetime import datetime, timedelta


class Conference:
    """
    Represents an academic conference with deadline and capacity management.

    Attributes:
        name (str): Full conference name.
        acronym (str): Short conference acronym.
        tracks (list): List of conference track names.
        topics (list): List of accepted topic keywords.
        deadlines (dict): Named deadline dates.
        max_papers (int): Maximum number of paper submissions.
    """

    # Valid conference statuses
    VALID_STATUSES = ['setup', 'open', 'reviewing', 'decided', 'archived']

    def __init__(self, name, acronym, tracks=None, topics=None,
                 max_papers=100):
        """
        Initialize a Conference instance.

        Args:
            name (str): Full conference name.
            acronym (str): Short acronym (e.g., 'ICSE').
            tracks (list): List of track names.
            topics (list): List of accepted topics.
            max_papers (int): Maximum submissions allowed.
        """
        self.name = name
        self.acronym = acronym
        self.tracks = tracks or []
        self.topics = [t.lower().strip() for t in (topics or [])]
        self.max_papers = max_papers
        self.deadlines = {}
        self.submissions = []
        self.status = 'setup'
        self.created_at = datetime.utcnow()

    def set_deadline(self, deadline_name, deadline_date):
        """
        Set a named deadline for the conference.

        Args:
            deadline_name (str): Name of the deadline (e.g., 'submission', 'review').
            deadline_date (datetime): Deadline datetime.

        Returns:
            bool: True if the deadline was set successfully.

        Raises:
            ValueError: If the deadline date is in the past.
        """
        if isinstance(deadline_date, str):
            deadline_date = datetime.fromisoformat(deadline_date)

        self.deadlines[deadline_name] = deadline_date
        return True

    def check_deadline(self, deadline_name):
        """
        Check the status of a specific deadline.

        Args:
            deadline_name (str): Name of the deadline to check.

        Returns:
            dict: Deadline status with time remaining or time elapsed.
        """
        if deadline_name not in self.deadlines:
            return {'exists': False, 'message': f'Deadline "{deadline_name}" not set.'}

        deadline = self.deadlines[deadline_name]
        now = datetime.utcnow()
        diff = deadline - now

        if diff.total_seconds() > 0:
            days = diff.days
            hours = diff.seconds // 3600
            return {
                'exists': True,
                'deadline': deadline.isoformat(),
                'passed': False,
                'days_remaining': days,
                'hours_remaining': hours,
                'message': f'{days} days and {hours} hours remaining.'
            }
        else:
            days_ago = abs(diff.days)
            return {
                'exists': True,
                'deadline': deadline.isoformat(),
                'passed': True,
                'days_elapsed': days_ago,
                'message': f'Deadline passed {days_ago} days ago.'
            }

    def is_submission_open(self):
        """
        Check if the submission deadline has not yet passed.

        Returns:
            bool: True if submissions are still accepted.
        """
        if 'submission' not in self.deadlines:
            return self.status == 'open'

        now = datetime.utcnow()
        return now < self.deadlines['submission'] and self.status in ('setup', 'open')

    def has_capacity(self):
        """
        Check if the conference can still accept more submissions.

        Returns:
            bool: True if current submissions are below the maximum.
        """
        return len(self.submissions) < self.max_papers

    def add_submission(self, paper_id):
        """
        Register a paper submission to this conference.

        Args:
            paper_id: Identifier of the submitted paper.

        Returns:
            dict: Submission result with status.
        """
        if not self.has_capacity():
            return {
                'accepted': False,
                'reason': f'Conference at maximum capacity ({self.max_papers} papers).'
            }

        if paper_id in self.submissions:
            return {
                'accepted': False,
                'reason': 'Paper already submitted to this conference.'
            }

        self.submissions.append(paper_id)
        return {
            'accepted': True,
            'paper_id': paper_id,
            'submission_number': len(self.submissions),
            'remaining_capacity': self.max_papers - len(self.submissions)
        }

    def add_track(self, track_name):
        """
        Add a new track to the conference.

        Args:
            track_name (str): Name of the track to add.

        Returns:
            bool: True if the track was added, False if it already exists.
        """
        if track_name in self.tracks:
            return False
        self.tracks.append(track_name)
        return True

    def remove_track(self, track_name):
        """
        Remove a track from the conference.

        Args:
            track_name (str): Name of the track to remove.

        Returns:
            bool: True if the track was removed.
        """
        if track_name in self.tracks:
            self.tracks.remove(track_name)
            return True
        return False

    def is_topic_relevant(self, paper_keywords):
        """
        Check if a paper's keywords are relevant to the conference topics.

        Args:
            paper_keywords (list): List of paper keywords.

        Returns:
            dict: Relevance result with match score.
        """
        if not self.topics or not paper_keywords:
            return {'relevant': True, 'score': 0.0, 'matched_topics': []}

        paper_kw = {k.lower().strip() for k in paper_keywords}
        matched = []

        for topic in self.topics:
            for kw in paper_kw:
                if topic in kw or kw in topic:
                    matched.append(topic)
                    break

        score = len(matched) / len(self.topics) if self.topics else 0.0

        return {
            'relevant': score > 0,
            'score': round(score, 3),
            'matched_topics': matched,
            'total_topics': len(self.topics)
        }

    def get_capacity_report(self):
        """
        Generate a capacity planning report for the conference.

        Returns:
            dict: Capacity report with current usage and projections.
        """
        current = len(self.submissions)
        utilization = round(current / self.max_papers * 100, 1) if self.max_papers > 0 else 0

        return {
            'conference': self.acronym,
            'max_papers': self.max_papers,
            'current_submissions': current,
            'remaining_slots': self.max_papers - current,
            'utilization_percent': utilization,
            'tracks': len(self.tracks),
            'topics': len(self.topics),
            'status': self.status
        }

    def advance_status(self):
        """
        Move the conference to the next lifecycle status.

        Returns:
            str: The new status after advancement.
        """
        current_index = self.VALID_STATUSES.index(self.status)
        if current_index < len(self.VALID_STATUSES) - 1:
            self.status = self.VALID_STATUSES[current_index + 1]
        return self.status

    def get_timeline(self):
        """
        Get an ordered timeline of all conference deadlines.

        Returns:
            list: List of deadline dicts sorted by date.
        """
        timeline = []
        for name, date in self.deadlines.items():
            timeline.append({
                'name': name,
                'date': date.isoformat(),
                'status': self.check_deadline(name)
            })
        timeline.sort(key=lambda x: x['date'])
        return timeline

    def __repr__(self):
        return f'Conference("{self.acronym}", tracks={len(self.tracks)}, status={self.status})'
