"""
Author model representing a paper author or contributor.
Stores profile information, affiliations, and publication history.
"""

from datetime import datetime
from .database import db


class Author(db.Model):
    """
    Represents an author who can submit papers to conferences.
    Stores personal details, affiliation, and expertise areas.
    """

    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    affiliation = db.Column(db.String(255), nullable=True)  # University or organization
    department = db.Column(db.String(255), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    orcid = db.Column(db.String(50), nullable=True)  # ORCID identifier
    expertise = db.Column(db.Text, nullable=True)  # Comma-separated expertise areas
    bio = db.Column(db.Text, nullable=True)
    h_index = db.Column(db.Integer, nullable=True)  # Academic h-index
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to papers
    papers = db.relationship('Paper', backref='author', lazy=True)

    def to_dict(self):
        """
        Serialize author instance to a dictionary for JSON responses.

        Returns:
            dict: Author data with all profile fields and paper count.
        """
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'affiliation': self.affiliation,
            'department': self.department,
            'country': self.country,
            'orcid': self.orcid,
            'expertise': self.expertise,
            'bio': self.bio,
            'h_index': self.h_index,
            'paper_count': len(self.papers) if self.papers else 0,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def full_name(self):
        """Return the author's full name."""
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'<Author {self.id}: {self.full_name}>'
