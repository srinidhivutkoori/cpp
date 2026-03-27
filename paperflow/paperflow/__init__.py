"""
PaperFlow - Academic Conference Paper Management Library.

A comprehensive OOP library for managing academic conference paper submissions,
peer reviews, and decision workflows. Developed as part of the Cloud Platform
Programming MSc project at National College of Ireland.

Author: Srinidhi Vutkoori (X25173243)
"""

from .paper import Paper
from .reviewer import Reviewer
from .conference import Conference
from .submission import Submission
from .scoring import Scoring

__version__ = '1.0.0'
__author__ = 'Srinidhi Vutkoori'
__all__ = ['Paper', 'Reviewer', 'Conference', 'Submission', 'Scoring']
