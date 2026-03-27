"""
confmanager - Academic Conference Paper Submission System Library

A Python library for managing academic conference paper submissions,
reviews, and conference organisation.
"""

__version__ = "1.0.0"
__author__ = "Srinidhi Vutkoori"

from confmanager.paper import PaperManager
from confmanager.reviewer import ReviewManager
from confmanager.conference import ConferenceManager
from confmanager.formatter import PaperFormatter

__all__ = [
    "PaperManager",
    "ReviewManager",
    "ConferenceManager",
    "PaperFormatter",
]
