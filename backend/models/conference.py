"""
Conference model representing an academic conference with tracks, deadlines, and topics.
Supports full CRUD operations via SQLAlchemy ORM.
"""

from datetime import datetime
from .database import db


class Conference(db.Model):
    """
    Represents an academic conference where papers can be submitted.
    Stores metadata including name, description, deadlines, tracks, and topics.
    """

    __tablename__ = 'conferences'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    acronym = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    website = db.Column(db.String(500), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    submission_deadline = db.Column(db.String(20), nullable=False)
    review_deadline = db.Column(db.String(20), nullable=True)
    notification_date = db.Column(db.String(20), nullable=True)
    tracks = db.Column(db.Text, nullable=True)  # JSON string of track names
    topics = db.Column(db.Text, nullable=True)   # JSON string of topic keywords
    max_papers = db.Column(db.Integer, default=100)
    status = db.Column(db.String(50), default='open')  # open, closed, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to papers submitted to this conference
    papers = db.relationship('Paper', backref='conference', lazy=True)

    def to_dict(self):
        """
        Serialize conference instance to a dictionary for JSON responses.

        Returns:
            dict: Conference data with all fields including related paper count.
        """
        return {
            'id': self.id,
            'name': self.name,
            'acronym': self.acronym,
            'description': self.description,
            'website': self.website,
            'location': self.location,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'submission_deadline': self.submission_deadline,
            'review_deadline': self.review_deadline,
            'notification_date': self.notification_date,
            'tracks': self.tracks,
            'topics': self.topics,
            'max_papers': self.max_papers,
            'status': self.status,
            'paper_count': len(self.papers) if self.papers else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self):
        return f'<Conference {self.acronym}: {self.name}>'
