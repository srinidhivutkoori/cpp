"""
Review model representing a peer review of a submitted paper.
Stores reviewer scores, comments, and recommendation decisions.
"""

from datetime import datetime
from .database import db


class Review(db.Model):
    """
    Represents a peer review for a submitted paper.
    Captures scores across multiple dimensions and reviewer feedback.
    """

    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    reviewer_name = db.Column(db.String(255), nullable=False)
    reviewer_email = db.Column(db.String(255), nullable=False)
    reviewer_expertise = db.Column(db.String(100), nullable=True)  # Area of expertise

    # Scoring dimensions (1-10 scale)
    originality_score = db.Column(db.Integer, nullable=True)
    significance_score = db.Column(db.Integer, nullable=True)
    clarity_score = db.Column(db.Integer, nullable=True)
    methodology_score = db.Column(db.Integer, nullable=True)
    overall_score = db.Column(db.Integer, nullable=True)

    # Reviewer feedback
    summary_comment = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.Text, nullable=True)
    weaknesses = db.Column(db.Text, nullable=True)
    detailed_comments = db.Column(db.Text, nullable=True)
    confidential_comments = db.Column(db.Text, nullable=True)  # Comments for editors only

    # Recommendation: strong_accept, accept, weak_accept, borderline, weak_reject, reject, strong_reject
    recommendation = db.Column(db.String(50), nullable=True)
    confidence = db.Column(db.Integer, nullable=True)  # 1-5 reviewer confidence level

    # Foreign key
    paper_id = db.Column(db.Integer, db.ForeignKey('papers.id'), nullable=False)

    # Status tracking
    status = db.Column(db.String(50), default='assigned')  # assigned, in_progress, completed
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """
        Serialize review instance to a dictionary for JSON responses.

        Returns:
            dict: Review data with all scores and feedback fields.
        """
        return {
            'id': self.id,
            'reviewer_name': self.reviewer_name,
            'reviewer_email': self.reviewer_email,
            'reviewer_expertise': self.reviewer_expertise,
            'originality_score': self.originality_score,
            'significance_score': self.significance_score,
            'clarity_score': self.clarity_score,
            'methodology_score': self.methodology_score,
            'overall_score': self.overall_score,
            'summary_comment': self.summary_comment,
            'strengths': self.strengths,
            'weaknesses': self.weaknesses,
            'detailed_comments': self.detailed_comments,
            'confidential_comments': self.confidential_comments,
            'recommendation': self.recommendation,
            'confidence': self.confidence,
            'paper_id': self.paper_id,
            'status': self.status,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Review {self.id} by {self.reviewer_name}>'
