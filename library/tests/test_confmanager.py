"""
Unit tests for the confmanager library.
"""

import unittest
from datetime import datetime, timedelta

from confmanager.paper import PaperManager
from confmanager.reviewer import ReviewManager
from confmanager.conference import ConferenceManager
from confmanager.formatter import PaperFormatter


class TestPaperManager(unittest.TestCase):
    """Tests for PaperManager."""

    def setUp(self):
        self.pm = PaperManager()

    def test_generate_paper_id_format(self):
        pid = self.pm.generate_paper_id("ICSE")
        self.assertTrue(pid.startswith("PAPER-ICSE-"))
        parts = pid.split("-")
        self.assertEqual(len(parts), 4)
        self.assertEqual(len(parts[3]), 4)  # random 4 digits

    def test_generate_paper_id_uppercase(self):
        pid = self.pm.generate_paper_id("conf")
        self.assertIn("CONF", pid)

    def test_validate_paper_valid(self):
        data = {
            "title": "A Valid Paper Title Here",
            "abstract": "A" * 100,
            "authors": ["Alice"],
            "keywords": ["testing"],
        }
        valid, errors = self.pm.validate_paper(data)
        self.assertTrue(valid)
        self.assertEqual(errors, [])

    def test_validate_paper_title_too_short(self):
        data = {
            "title": "Short",
            "abstract": "A" * 100,
            "authors": ["Alice"],
            "keywords": ["testing"],
        }
        valid, errors = self.pm.validate_paper(data)
        self.assertFalse(valid)
        self.assertTrue(any("Title" in e for e in errors))

    def test_validate_paper_missing_authors(self):
        data = {
            "title": "A Valid Paper Title Here",
            "abstract": "A" * 100,
            "authors": [],
            "keywords": ["testing"],
        }
        valid, errors = self.pm.validate_paper(data)
        self.assertFalse(valid)
        self.assertTrue(any("author" in e.lower() for e in errors))

    def test_validate_paper_missing_abstract(self):
        data = {
            "title": "A Valid Paper Title Here",
            "abstract": "Short",
            "authors": ["Alice"],
            "keywords": ["testing"],
        }
        valid, errors = self.pm.validate_paper(data)
        self.assertFalse(valid)
        self.assertTrue(any("Abstract" in e for e in errors))

    def test_validate_paper_missing_keywords(self):
        data = {
            "title": "A Valid Paper Title Here",
            "abstract": "A" * 100,
            "authors": ["Alice"],
            "keywords": [],
        }
        valid, errors = self.pm.validate_paper(data)
        self.assertFalse(valid)
        self.assertTrue(any("keyword" in e.lower() for e in errors))

    def test_get_paper_status_flow(self):
        flow = self.pm.get_paper_status_flow()
        self.assertIn("submitted", flow)
        self.assertIn("under_review", flow["submitted"])

    def test_validate_status_transition_valid(self):
        self.assertTrue(self.pm.validate_status_transition("submitted", "under_review"))

    def test_validate_status_transition_invalid(self):
        self.assertFalse(self.pm.validate_status_transition("submitted", "accepted"))

    def test_validate_status_transition_revision_flow(self):
        self.assertTrue(self.pm.validate_status_transition("under_review", "revision_required"))
        self.assertTrue(self.pm.validate_status_transition("revision_required", "resubmitted"))
        self.assertTrue(self.pm.validate_status_transition("resubmitted", "under_review"))

    def test_calculate_review_score(self):
        reviews = [{"score": 8}, {"score": 6}, {"score": 7}]
        self.assertEqual(self.pm.calculate_review_score(reviews), 7.0)

    def test_calculate_review_score_empty(self):
        self.assertEqual(self.pm.calculate_review_score([]), 0.0)

    def test_format_citation_ieee(self):
        paper = {
            "authors": ["A. Smith", "B. Jones"],
            "title": "A Great Paper",
            "conference": "ICSE 2026",
            "year": 2026,
            "pages": "1-10",
        }
        cit = self.pm.format_citation(paper, style="ieee")
        self.assertIn('"A Great Paper,"', cit)
        self.assertIn("pp. 1-10", cit)

    def test_format_citation_apa(self):
        paper = {
            "authors": ["A. Smith"],
            "title": "A Great Paper",
            "conference": "ICSE 2026",
            "year": 2026,
        }
        cit = self.pm.format_citation(paper, style="apa")
        self.assertIn("(2026)", cit)


class TestReviewManager(unittest.TestCase):
    """Tests for ReviewManager."""

    def setUp(self):
        self.rm = ReviewManager()

    def test_assign_reviewers_basic(self):
        paper = {"authors": ["Alice"]}
        reviewers = ["Bob", "Carol", "Dave", "Eve", "Frank"]
        assigned = self.rm.assign_reviewers(paper, reviewers, count=3)
        self.assertEqual(len(assigned), 3)
        self.assertNotIn("Alice", assigned)

    def test_assign_reviewers_conflict_avoidance(self):
        paper = {"authors": ["Alice", "Bob"]}
        reviewers = ["Alice", "Bob", "Carol", "Dave"]
        assigned = self.rm.assign_reviewers(paper, reviewers, count=3)
        self.assertNotIn("Alice", assigned)
        self.assertNotIn("Bob", assigned)

    def test_assign_reviewers_insufficient_pool(self):
        paper = {"authors": ["Alice"]}
        reviewers = ["Bob", "Carol"]
        assigned = self.rm.assign_reviewers(paper, reviewers, count=5)
        self.assertEqual(len(assigned), 2)

    def test_validate_review_valid(self):
        data = {
            "score": 7,
            "comments": "A" * 60,
            "recommendation": "accept",
        }
        valid, errors = self.rm.validate_review(data)
        self.assertTrue(valid)

    def test_validate_review_invalid_score(self):
        data = {"score": 11, "comments": "A" * 60, "recommendation": "accept"}
        valid, errors = self.rm.validate_review(data)
        self.assertFalse(valid)

    def test_validate_review_short_comments(self):
        data = {"score": 5, "comments": "Short", "recommendation": "accept"}
        valid, errors = self.rm.validate_review(data)
        self.assertFalse(valid)

    def test_validate_review_bad_recommendation(self):
        data = {"score": 5, "comments": "A" * 60, "recommendation": "maybe"}
        valid, errors = self.rm.validate_review(data)
        self.assertFalse(valid)

    def test_calculate_acceptance_rate(self):
        papers = [
            {"status": "accepted"},
            {"status": "rejected"},
            {"status": "accepted"},
            {"status": "rejected"},
        ]
        self.assertEqual(self.rm.calculate_acceptance_rate(papers), 50.0)

    def test_calculate_acceptance_rate_empty(self):
        self.assertEqual(self.rm.calculate_acceptance_rate([]), 0.0)

    def test_get_review_stats(self):
        reviews = [
            {"score": 8, "recommendation": "accept"},
            {"score": 4, "recommendation": "reject"},
            {"score": 6, "recommendation": "accept"},
        ]
        stats = self.rm.get_review_stats(reviews)
        self.assertEqual(stats["count"], 3)
        self.assertEqual(stats["min_score"], 4)
        self.assertEqual(stats["max_score"], 8)
        self.assertEqual(stats["avg_score"], 6.0)
        self.assertEqual(stats["recommendation_breakdown"]["accept"], 2)

    def test_get_review_stats_empty(self):
        stats = self.rm.get_review_stats([])
        self.assertEqual(stats["count"], 0)

    def test_check_review_deadline_overdue(self):
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertTrue(self.rm.check_review_deadline({}, yesterday))

    def test_check_review_deadline_not_overdue(self):
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertFalse(self.rm.check_review_deadline({}, tomorrow))


class TestConferenceManager(unittest.TestCase):
    """Tests for ConferenceManager."""

    def setUp(self):
        self.cm = ConferenceManager()

    def test_validate_conference_valid(self):
        data = {
            "name": "ICSE 2026",
            "description": "Top SE conference",
            "startDate": "2026-06-01",
            "endDate": "2026-06-05",
            "submissionDeadline": "2026-03-01",
        }
        valid, errors = self.cm.validate_conference(data)
        self.assertTrue(valid)

    def test_validate_conference_end_before_start(self):
        data = {
            "name": "ICSE 2026",
            "description": "A conference",
            "startDate": "2026-06-05",
            "endDate": "2026-06-01",
            "submissionDeadline": "2026-03-01",
        }
        valid, errors = self.cm.validate_conference(data)
        self.assertFalse(valid)
        self.assertTrue(any("End date" in e for e in errors))

    def test_validate_conference_missing_name(self):
        data = {
            "name": "",
            "description": "A conference",
            "startDate": "2026-06-01",
            "endDate": "2026-06-05",
            "submissionDeadline": "2026-03-01",
        }
        valid, errors = self.cm.validate_conference(data)
        self.assertFalse(valid)

    def test_is_submission_open_true(self):
        future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.assertTrue(self.cm.is_submission_open({"submissionDeadline": future}))

    def test_is_submission_open_false(self):
        past = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        self.assertFalse(self.cm.is_submission_open({"submissionDeadline": past}))

    def test_get_conference_stats(self):
        papers = [
            {"status": "accepted"},
            {"status": "accepted"},
            {"status": "rejected"},
            {"status": "under_review"},
        ]
        stats = self.cm.get_conference_stats(papers)
        self.assertEqual(stats["total_submissions"], 4)
        self.assertEqual(stats["accepted"], 2)
        self.assertEqual(stats["rejected"], 1)
        self.assertEqual(stats["pending"], 1)
        self.assertEqual(stats["acceptance_rate"], 50.0)

    def test_generate_conference_report(self):
        conf = {"name": "ICSE 2026", "startDate": "2026-06-01", "endDate": "2026-06-05"}
        papers = [{"status": "accepted"}, {"status": "rejected"}]
        report = self.cm.generate_conference_report(conf, papers)
        self.assertIn("ICSE 2026", report)
        self.assertIn("Total Submissions: 2", report)

    def test_format_schedule(self):
        sessions = [
            {"time": "09:00", "title": "Keynote", "speaker": "Dr. X", "room": "A1"},
        ]
        schedule = self.cm.format_schedule(sessions)
        self.assertIn("Keynote", schedule)
        self.assertIn("Dr. X", schedule)


class TestPaperFormatter(unittest.TestCase):
    """Tests for PaperFormatter."""

    def setUp(self):
        self.pf = PaperFormatter()

    def test_format_paper_summary(self):
        paper = {"title": "My Paper", "authors": ["Alice"], "status": "accepted"}
        summary = self.pf.format_paper_summary(paper)
        self.assertIn("[ACCEPTED]", summary)
        self.assertIn("My Paper", summary)

    def test_format_paper_detail_no_reviews(self):
        paper = {
            "title": "My Paper",
            "authors": ["Alice"],
            "status": "submitted",
            "keywords": ["AI"],
            "abstract": "Some abstract text.",
        }
        detail = self.pf.format_paper_detail(paper)
        self.assertIn("My Paper", detail)
        self.assertIn("Alice", detail)

    def test_format_paper_detail_with_reviews(self):
        paper = {
            "title": "My Paper",
            "authors": ["Alice"],
            "status": "under_review",
            "keywords": ["AI"],
            "abstract": "Some abstract text.",
        }
        reviews = [{"score": 7, "recommendation": "accept", "comments": "Good work"}]
        detail = self.pf.format_paper_detail(paper, reviews)
        self.assertIn("Reviews (1)", detail)
        self.assertIn("7/10", detail)

    def test_to_csv(self):
        papers = [
            {
                "title": "Paper One",
                "authors": ["Alice", "Bob"],
                "status": "accepted",
                "score": 8.5,
                "keywords": ["AI", "ML"],
                "submitted_date": "2026-01-15",
            }
        ]
        csv_str = self.pf.to_csv(papers)
        self.assertIn("title,authors,status,score,keywords,submitted_date", csv_str)
        self.assertIn("Paper One", csv_str)
        self.assertIn("Alice; Bob", csv_str)

    def test_format_acceptance_letter(self):
        paper = {"title": "Great Paper", "authors": ["Alice"]}
        conf = {"name": "ICSE 2026", "startDate": "2026-06-01", "endDate": "2026-06-05"}
        letter = self.pf.format_acceptance_letter(paper, conf)
        self.assertIn("ACCEPTED", letter)
        self.assertIn("Great Paper", letter)

    def test_format_rejection_letter(self):
        paper = {
            "title": "My Paper",
            "authors": ["Alice"],
            "reviews": [{"score": 3, "comments": "Needs more work."}],
        }
        conf = {"name": "ICSE 2026"}
        letter = self.pf.format_rejection_letter(paper, conf)
        self.assertIn("not been accepted", letter)
        self.assertIn("Reviewer 1", letter)

    def test_format_rejection_letter_no_reviews(self):
        paper = {"title": "My Paper", "authors": ["Alice"]}
        conf = {"name": "ICSE 2026"}
        letter = self.pf.format_rejection_letter(paper, conf)
        self.assertIn("not been accepted", letter)


if __name__ == "__main__":
    unittest.main()
