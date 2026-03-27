"""Tests for the ConferenceManager class."""

from confmanager.conference import ConferenceManager


class TestConferenceManager:
    """Test suite for ConferenceManager."""

    def setup_method(self):
        self.cm = ConferenceManager()

    def test_validate_conference_valid(self):
        data = {
            "name": "ICSE 2026",
            "description": "International Conference on Software Engineering",
            "startDate": "2026-06-01",
            "endDate": "2026-06-05",
            "submissionDeadline": "2026-03-01",
        }
        is_valid, errors = self.cm.validate_conference(data)
        assert is_valid is True
        assert errors == []

    def test_validate_conference_missing_name(self):
        data = {
            "name": "",
            "description": "Desc",
            "startDate": "2026-06-01",
            "endDate": "2026-06-05",
            "submissionDeadline": "2026-03-01",
        }
        is_valid, errors = self.cm.validate_conference(data)
        assert is_valid is False

    def test_validate_conference_end_before_start(self):
        data = {
            "name": "Test",
            "description": "Desc",
            "startDate": "2026-06-05",
            "endDate": "2026-06-01",
            "submissionDeadline": "2026-03-01",
        }
        is_valid, errors = self.cm.validate_conference(data)
        assert is_valid is False
        assert any("End date" in e for e in errors)

    def test_get_conference_stats(self):
        papers = [
            {"status": "accepted"},
            {"status": "accepted"},
            {"status": "rejected"},
            {"status": "under_review"},
        ]
        stats = self.cm.get_conference_stats(papers)
        assert stats["total_submissions"] == 4
        assert stats["accepted"] == 2
        assert stats["rejected"] == 1
        assert stats["pending"] == 1
        assert stats["acceptance_rate"] == 50.0

    def test_get_conference_stats_empty(self):
        stats = self.cm.get_conference_stats([])
        assert stats["total_submissions"] == 0
        assert stats["acceptance_rate"] == 0.0

    def test_generate_conference_report(self):
        conf = {"name": "ICSE 2026", "startDate": "2026-06-01", "endDate": "2026-06-05"}
        papers = [{"status": "accepted"}, {"status": "rejected"}]
        report = self.cm.generate_conference_report(conf, papers)
        assert "ICSE 2026" in report
        assert "Total Submissions: 2" in report

    def test_format_schedule(self):
        sessions = [
            {"time": "09:00", "title": "Keynote", "speaker": "Dr. Smith", "room": "A1"}
        ]
        schedule = self.cm.format_schedule(sessions)
        assert "Keynote" in schedule
        assert "Dr. Smith" in schedule
