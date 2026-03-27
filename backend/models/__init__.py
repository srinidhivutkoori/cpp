"""
Models package for the Academic Conference Paper Submission System.
Contains SQLAlchemy models for conferences, papers, reviews, and authors.
"""

from .database import db
from .conference import Conference
from .paper import Paper
from .review import Review
from .author import Author

__all__ = ['db', 'Conference', 'Paper', 'Review', 'Author']
