"""
Submission class for managing paper submission workflow states and tracking.
Handles the complete lifecycle from submission through review to final decision.
"""

from datetime import datetime


class Submission:
    """
    Manages the workflow of a paper submission through the review process.

    The workflow follows: submitted -> under_review -> accepted/rejected.
    Tracks all state transitions with timestamps for audit purposes.

    Attributes:
        paper_id: Identifier of the submitted paper.
        conference_id: Identifier of the target conference.
        author_id: Identifier of the submitting author.
        status (str): Current workflow status.
        history (list): List of state transition records.
    """

    # Valid workflow states and their allowed transitions
    WORKFLOW_STATES = {
        'draft': ['submitted'],
        'submitted': ['under_review', 'withdrawn'],
        'under_review': ['revision_requested', 'accepted', 'rejected'],
        'revision_requested': ['submitted', 'withdrawn'],
        'accepted': ['camera_ready'],
        'rejected': [],
        'withdrawn': [],
        'camera_ready': ['published']
    }

    def __init__(self, paper_id, conference_id, author_id, status='draft'):
        """
        Initialize a Submission with the given identifiers.

        Args:
            paper_id: Paper identifier.
            conference_id: Conference identifier.
            author_id: Author identifier.
            status (str): Initial workflow status.
        """
        self.paper_id = paper_id
        self.conference_id = conference_id
        self.author_id = author_id
        self.status = status
        self.history = [{
            'from_status': None,
            'to_status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'notes': 'Submission initialized.'
        }]
        self.reviewers_assigned = []
        self.decision = None
        self.decision_notes = ''
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def transition_to(self, new_status, notes=''):
        """
        Transition the submission to a new workflow state.

        Args:
            new_status (str): Target state.
            notes (str): Optional notes about the transition.

        Returns:
            dict: Transition result with success status.

        Raises:
            ValueError: If the transition is not allowed.
        """
        allowed = self.WORKFLOW_STATES.get(self.status, [])

        if new_status not in allowed:
            return {
                'success': False,
                'error': f'Cannot transition from "{self.status}" to "{new_status}". '
                         f'Allowed transitions: {allowed}'
            }

        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.utcnow()

        transition_record = {
            'from_status': old_status,
            'to_status': new_status,
            'timestamp': self.updated_at.isoformat(),
            'notes': notes
        }
        self.history.append(transition_record)

        return {
            'success': True,
            'previous_status': old_status,
            'current_status': new_status,
            'transition': transition_record
        }

    def submit(self):
        """
        Submit the paper for review consideration.

        Returns:
            dict: Transition result.
        """
        return self.transition_to('submitted', 'Paper submitted for review.')

    def start_review(self):
        """
        Move the submission into the review phase.

        Returns:
            dict: Transition result.
        """
        return self.transition_to('under_review', 'Review process initiated.')

    def accept(self, notes=''):
        """
        Accept the submitted paper.

        Args:
            notes (str): Acceptance notes.

        Returns:
            dict: Transition result.
        """
        self.decision = 'accepted'
        self.decision_notes = notes
        return self.transition_to('accepted', notes or 'Paper accepted.')

    def reject(self, notes=''):
        """
        Reject the submitted paper.

        Args:
            notes (str): Rejection notes.

        Returns:
            dict: Transition result.
        """
        self.decision = 'rejected'
        self.decision_notes = notes
        return self.transition_to('rejected', notes or 'Paper rejected.')

    def request_revision(self, notes=''):
        """
        Request revisions from the author.

        Args:
            notes (str): Revision instructions.

        Returns:
            dict: Transition result.
        """
        return self.transition_to('revision_requested', notes or 'Revisions requested.')

    def withdraw(self, notes=''):
        """
        Withdraw the submission.

        Args:
            notes (str): Withdrawal reason.

        Returns:
            dict: Transition result.
        """
        return self.transition_to('withdrawn', notes or 'Submission withdrawn by author.')

    def assign_reviewer(self, reviewer_id):
        """
        Assign a reviewer to this submission.

        Args:
            reviewer_id: Identifier of the reviewer to assign.

        Returns:
            bool: True if the reviewer was assigned, False if already assigned.
        """
        if reviewer_id not in self.reviewers_assigned:
            self.reviewers_assigned.append(reviewer_id)
            return True
        return False

    def get_allowed_transitions(self):
        """
        Get the list of valid state transitions from the current status.

        Returns:
            list: List of allowed next states.
        """
        return self.WORKFLOW_STATES.get(self.status, [])

    def is_terminal(self):
        """
        Check if the submission is in a terminal (final) state.

        Returns:
            bool: True if no further transitions are possible.
        """
        return len(self.get_allowed_transitions()) == 0

    def get_duration(self):
        """
        Calculate the time elapsed since submission was created.

        Returns:
            dict: Duration information in days and hours.
        """
        elapsed = datetime.utcnow() - self.created_at
        return {
            'days': elapsed.days,
            'hours': elapsed.seconds // 3600,
            'total_seconds': int(elapsed.total_seconds())
        }

    def get_status_report(self):
        """
        Generate a comprehensive status report for the submission.

        Returns:
            dict: Complete submission status with history.
        """
        return {
            'paper_id': self.paper_id,
            'conference_id': self.conference_id,
            'author_id': self.author_id,
            'current_status': self.status,
            'decision': self.decision,
            'decision_notes': self.decision_notes,
            'reviewers_assigned': len(self.reviewers_assigned),
            'is_terminal': self.is_terminal(),
            'allowed_transitions': self.get_allowed_transitions(),
            'history_length': len(self.history),
            'history': self.history,
            'duration': self.get_duration(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

    def __repr__(self):
        return f'Submission(paper={self.paper_id}, status="{self.status}")'
