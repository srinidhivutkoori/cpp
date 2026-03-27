"""
Unit tests for the Conference class.
Tests deadline management, track organization, and capacity planning.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from paperflow.conference import Conference


class TestDeadlineManagement:
    """Tests for conference deadline operations."""

    def test_set_deadline(self):
        """Test setting a deadline."""
        conf = Conference("Test Conf", "TC")
        future = datetime.utcnow() + timedelta(days=30)
        result = conf.set_deadline('submission', future)
        assert result is True
        assert 'submission' in conf.deadlines

    def test_check_future_deadline(self):
        """Test checking a deadline that has not passed."""
        conf = Conference("Test Conf", "TC")
        future = datetime.utcnow() + timedelta(days=30)
        conf.set_deadline('submission', future)
        result = conf.check_deadline('submission')
        assert result['passed'] is False
        assert result['days_remaining'] >= 29

    def test_check_past_deadline(self):
        """Test checking a deadline that has passed."""
        conf = Conference("Test Conf", "TC")
        past = datetime.utcnow() - timedelta(days=5)
        conf.set_deadline('submission', past)
        result = conf.check_deadline('submission')
        assert result['passed'] is True

    def test_check_nonexistent_deadline(self):
        """Test checking a deadline that does not exist."""
        conf = Conference("Test Conf", "TC")
        result = conf.check_deadline('nonexistent')
        assert result['exists'] is False

    def test_is_submission_open(self):
        """Test submission open status with future deadline."""
        conf = Conference("Test Conf", "TC")
        conf.status = 'open'
        future = datetime.utcnow() + timedelta(days=30)
        conf.set_deadline('submission', future)
        assert conf.is_submission_open() is True

    def test_get_timeline(self):
        """Test getting an ordered timeline of deadlines."""
        conf = Conference("Test Conf", "TC")
        conf.set_deadline('submission', datetime.utcnow() + timedelta(days=10))
        conf.set_deadline('review', datetime.utcnow() + timedelta(days=30))
        timeline = conf.get_timeline()
        assert len(timeline) == 2
        assert timeline[0]['name'] == 'submission'


class TestTrackManagement:
    """Tests for conference track operations."""

    def test_add_track(self):
        """Test adding a new track."""
        conf = Conference("Test Conf", "TC")
        assert conf.add_track("Technical Track") is True
        assert "Technical Track" in conf.tracks

    def test_add_duplicate_track(self):
        """Test that duplicate tracks are rejected."""
        conf = Conference("Test Conf", "TC", tracks=["Technical Track"])
        assert conf.add_track("Technical Track") is False

    def test_remove_track(self):
        """Test removing an existing track."""
        conf = Conference("Test Conf", "TC", tracks=["Technical Track"])
        assert conf.remove_track("Technical Track") is True
        assert "Technical Track" not in conf.tracks


class TestCapacityPlanning:
    """Tests for conference capacity management."""

    def test_has_capacity(self):
        """Test capacity check with available slots."""
        conf = Conference("Test Conf", "TC", max_papers=10)
        assert conf.has_capacity() is True

    def test_at_capacity(self):
        """Test capacity check when full."""
        conf = Conference("Test Conf", "TC", max_papers=1)
        conf.add_submission(1)
        assert conf.has_capacity() is False

    def test_add_submission(self):
        """Test adding a paper submission."""
        conf = Conference("Test Conf", "TC", max_papers=10)
        result = conf.add_submission(1)
        assert result['accepted'] is True
        assert result['submission_number'] == 1

    def test_add_submission_at_capacity(self):
        """Test adding a submission when at capacity."""
        conf = Conference("Test Conf", "TC", max_papers=1)
        conf.add_submission(1)
        result = conf.add_submission(2)
        assert result['accepted'] is False

    def test_add_duplicate_submission(self):
        """Test that duplicate submissions are rejected."""
        conf = Conference("Test Conf", "TC", max_papers=10)
        conf.add_submission(1)
        result = conf.add_submission(1)
        assert result['accepted'] is False

    def test_capacity_report(self):
        """Test capacity report generation."""
        conf = Conference("Test Conf", "TC", max_papers=100,
                         tracks=["Track A", "Track B"])
        conf.add_submission(1)
        report = conf.get_capacity_report()
        assert report['current_submissions'] == 1
        assert report['remaining_slots'] == 99
        assert report['utilization_percent'] == 1.0

    def test_topic_relevance(self):
        """Test topic relevance checking."""
        conf = Conference("Test Conf", "TC", topics=["AI", "cloud", "NLP"])
        result = conf.is_topic_relevant(["AI", "machine learning"])
        assert result['relevant'] is True
        assert result['score'] > 0

    def test_advance_status(self):
        """Test conference status advancement."""
        conf = Conference("Test Conf", "TC")
        assert conf.status == 'setup'
        conf.advance_status()
        assert conf.status == 'open'
        conf.advance_status()
        assert conf.status == 'reviewing'
