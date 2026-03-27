"""
Unit tests for the Submission class.
Tests workflow state transitions, status tracking, and lifecycle management.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from paperflow.submission import Submission


class TestWorkflowTransitions:
    """Tests for submission workflow state machine."""

    def test_initial_state(self):
        """Test that a new submission starts in draft state."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        assert sub.status == 'draft'

    def test_submit(self):
        """Test transitioning from draft to submitted."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        result = sub.submit()
        assert result['success'] is True
        assert sub.status == 'submitted'

    def test_start_review(self):
        """Test transitioning from submitted to under_review."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        sub.submit()
        result = sub.start_review()
        assert result['success'] is True
        assert sub.status == 'under_review'

    def test_accept(self):
        """Test accepting a paper under review."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        sub.submit()
        sub.start_review()
        result = sub.accept("Excellent paper.")
        assert result['success'] is True
        assert sub.status == 'accepted'
        assert sub.decision == 'accepted'

    def test_reject(self):
        """Test rejecting a paper under review."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        sub.submit()
        sub.start_review()
        result = sub.reject("Does not meet standards.")
        assert result['success'] is True
        assert sub.status == 'rejected'
        assert sub.decision == 'rejected'

    def test_invalid_transition(self):
        """Test that invalid state transitions fail gracefully."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        result = sub.start_review()  # Cannot go from draft to under_review
        assert result['success'] is False

    def test_withdraw(self):
        """Test withdrawing a submitted paper."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        sub.submit()
        result = sub.withdraw("Changed research direction.")
        assert result['success'] is True
        assert sub.status == 'withdrawn'

    def test_request_revision(self):
        """Test requesting revisions."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        sub.submit()
        sub.start_review()
        result = sub.request_revision("Please add more experiments.")
        assert result['success'] is True
        assert sub.status == 'revision_requested'

    def test_resubmit_after_revision(self):
        """Test resubmitting after revision request."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        sub.submit()
        sub.start_review()
        sub.request_revision()
        result = sub.submit()
        assert result['success'] is True
        assert sub.status == 'submitted'


class TestStatusTracking:
    """Tests for submission status tracking features."""

    def test_history_tracking(self):
        """Test that all transitions are recorded in history."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        sub.submit()
        sub.start_review()
        assert len(sub.history) == 3  # init + submit + start_review

    def test_is_terminal_accepted(self):
        """Test terminal state detection for accepted papers."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        sub.submit()
        sub.start_review()
        sub.accept()
        # Accepted papers can go to camera_ready, so not terminal
        assert sub.is_terminal() is False

    def test_is_terminal_rejected(self):
        """Test terminal state detection for rejected papers."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        sub.submit()
        sub.start_review()
        sub.reject()
        assert sub.is_terminal() is True

    def test_allowed_transitions(self):
        """Test getting allowed transitions from current state."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        allowed = sub.get_allowed_transitions()
        assert 'submitted' in allowed

    def test_assign_reviewer(self):
        """Test assigning a reviewer to the submission."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        assert sub.assign_reviewer(10) is True
        assert 10 in sub.reviewers_assigned
        # Duplicate assignment should return False
        assert sub.assign_reviewer(10) is False

    def test_get_duration(self):
        """Test duration calculation."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        duration = sub.get_duration()
        assert 'days' in duration
        assert 'total_seconds' in duration

    def test_get_status_report(self):
        """Test comprehensive status report generation."""
        sub = Submission(paper_id=1, conference_id=1, author_id=1)
        sub.submit()
        report = sub.get_status_report()
        assert report['current_status'] == 'submitted'
        assert report['paper_id'] == 1
        assert 'history' in report
        assert 'allowed_transitions' in report
