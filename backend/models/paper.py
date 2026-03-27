"""
Paper model representing an academic paper submission.
Tracks metadata, file storage references, NLP analysis results, and review status.
"""

from datetime import datetime
from .database import db


class Paper(db.Model):
    """
    Represents a paper submitted to a conference.
    Stores title, abstract, authors, file reference, and analysis results.
    """

    __tablename__ = 'papers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(500), nullable=False)
    abstract = db.Column(db.Text, nullable=False)
    keywords = db.Column(db.Text, nullable=True)  # Comma-separated keywords
    track = db.Column(db.String(100), nullable=True)
    file_key = db.Column(db.String(500), nullable=True)  # S3 key for uploaded PDF
    file_name = db.Column(db.String(255), nullable=True)
    file_size = db.Column(db.Integer, nullable=True)  # File size in bytes
    page_count = db.Column(db.Integer, nullable=True)
    word_count = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), default='submitted')  # submitted, under_review, accepted, rejected
    decision_notes = db.Column(db.Text, nullable=True)

    # NLP analysis results from Amazon Comprehend
    nlp_keywords = db.Column(db.Text, nullable=True)  # JSON of extracted key phrases
    nlp_sentiment = db.Column(db.String(50), nullable=True)
    nlp_entities = db.Column(db.Text, nullable=True)  # JSON of detected entities

    # Foreign keys
    conference_id = db.Column(db.Integer, db.ForeignKey('conferences.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

    # Timestamps
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to reviews
    reviews = db.relationship('Review', backref='paper', lazy=True)

    def to_dict(self):
        """
        Serialize paper instance to a dictionary for JSON responses.

        Returns:
            dict: Paper data including NLP analysis and review statistics.
        """
        return {
            'id': self.id,
            'title': self.title,
            'abstract': self.abstract,
            'keywords': self.keywords,
            'track': self.track,
            'file_key': self.file_key,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'page_count': self.page_count,
            'word_count': self.word_count,
            'status': self.status,
            'decision_notes': self.decision_notes,
            'nlp_keywords': self.nlp_keywords,
            'nlp_sentiment': self.nlp_sentiment,
            'nlp_entities': self.nlp_entities,
            'conference_id': self.conference_id,
            'author_id': self.author_id,
            'review_count': len(self.reviews) if self.reviews else 0,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Paper {self.id}: {self.title[:50]}>'
