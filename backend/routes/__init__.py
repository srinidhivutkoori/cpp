"""
Routes package for the Academic Conference Paper Submission System.
Contains Flask blueprints for all CRUD operations and AWS service endpoints.
"""

from .conference_routes import conference_bp
from .paper_routes import paper_bp
from .review_routes import review_bp
from .author_routes import author_bp
from .aws_routes import aws_bp

__all__ = ['conference_bp', 'paper_bp', 'review_bp', 'author_bp', 'aws_bp']
