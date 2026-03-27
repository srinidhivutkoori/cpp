"""
Paper class for validating paper metadata, checking format, and estimating word count.
Provides comprehensive paper metadata validation and analysis utilities.
"""

import re
from datetime import datetime


class Paper:
    """
    Represents an academic paper with metadata validation and analysis capabilities.

    Attributes:
        title (str): Paper title.
        abstract (str): Paper abstract text.
        authors (list): List of author name strings.
        keywords (list): List of keyword strings.
        file_name (str): Name of the uploaded PDF file.
        page_count (int): Number of pages in the paper.
    """

    # Constants for validation thresholds
    MIN_TITLE_LENGTH = 10
    MAX_TITLE_LENGTH = 300
    MIN_ABSTRACT_WORDS = 50
    MAX_ABSTRACT_WORDS = 500
    MIN_KEYWORDS = 3
    MAX_KEYWORDS = 8
    ALLOWED_EXTENSIONS = {'.pdf'}
    MAX_FILE_SIZE_MB = 50

    def __init__(self, title, abstract, authors=None, keywords=None,
                 file_name=None, page_count=None):
        """
        Initialize a Paper instance with metadata.

        Args:
            title (str): Paper title.
            abstract (str): Paper abstract.
            authors (list): List of author names.
            keywords (list): List of keywords.
            file_name (str): Uploaded file name.
            page_count (int): Number of pages.
        """
        self.title = title.strip() if title else ''
        self.abstract = abstract.strip() if abstract else ''
        self.authors = authors or []
        self.keywords = keywords or []
        self.file_name = file_name
        self.page_count = page_count
        self.created_at = datetime.utcnow()

    def validate_title(self):
        """
        Validate the paper title against length and format requirements.

        Returns:
            tuple: (is_valid: bool, errors: list of error messages).
        """
        errors = []
        if len(self.title) < self.MIN_TITLE_LENGTH:
            errors.append(
                f'Title must be at least {self.MIN_TITLE_LENGTH} characters long.'
            )
        if len(self.title) > self.MAX_TITLE_LENGTH:
            errors.append(
                f'Title must not exceed {self.MAX_TITLE_LENGTH} characters.'
            )
        if self.title and not self.title[0].isupper():
            errors.append('Title should start with a capital letter.')

        return (len(errors) == 0, errors)

    def validate_abstract(self):
        """
        Validate the paper abstract against word count requirements.

        Returns:
            tuple: (is_valid: bool, errors: list of error messages).
        """
        errors = []
        word_count = self.estimate_word_count()

        if word_count < self.MIN_ABSTRACT_WORDS:
            errors.append(
                f'Abstract must contain at least {self.MIN_ABSTRACT_WORDS} words '
                f'(current: {word_count}).'
            )
        if word_count > self.MAX_ABSTRACT_WORDS:
            errors.append(
                f'Abstract must not exceed {self.MAX_ABSTRACT_WORDS} words '
                f'(current: {word_count}).'
            )

        return (len(errors) == 0, errors)

    def validate_keywords(self):
        """
        Validate the keyword list against count requirements.

        Returns:
            tuple: (is_valid: bool, errors: list of error messages).
        """
        errors = []

        if len(self.keywords) < self.MIN_KEYWORDS:
            errors.append(
                f'At least {self.MIN_KEYWORDS} keywords are required '
                f'(current: {len(self.keywords)}).'
            )
        if len(self.keywords) > self.MAX_KEYWORDS:
            errors.append(
                f'Maximum {self.MAX_KEYWORDS} keywords allowed '
                f'(current: {len(self.keywords)}).'
            )

        # Check for duplicate keywords (case-insensitive)
        lower_keywords = [k.lower().strip() for k in self.keywords]
        if len(lower_keywords) != len(set(lower_keywords)):
            errors.append('Keywords must be unique (no duplicates).')

        return (len(errors) == 0, errors)

    def validate_file_format(self):
        """
        Validate the uploaded file format and name.

        Returns:
            tuple: (is_valid: bool, errors: list of error messages).
        """
        errors = []

        if not self.file_name:
            errors.append('No file uploaded.')
            return (False, errors)

        # Check file extension
        extension = '.' + self.file_name.rsplit('.', 1)[-1].lower() if '.' in self.file_name else ''
        if extension not in self.ALLOWED_EXTENSIONS:
            errors.append(f'Only PDF files are accepted. Got: {extension}')

        # Check for special characters in filename
        clean_name = re.sub(r'[^\w\s\-\.]', '', self.file_name)
        if clean_name != self.file_name:
            errors.append('File name contains invalid characters.')

        return (len(errors) == 0, errors)

    def validate_all(self):
        """
        Run all validation checks and return a comprehensive report.

        Returns:
            dict: Validation report with results for each check.
        """
        title_valid, title_errors = self.validate_title()
        abstract_valid, abstract_errors = self.validate_abstract()
        keywords_valid, keywords_errors = self.validate_keywords()
        file_valid, file_errors = self.validate_file_format()

        all_valid = title_valid and abstract_valid and keywords_valid and file_valid

        return {
            'is_valid': all_valid,
            'title': {'valid': title_valid, 'errors': title_errors},
            'abstract': {'valid': abstract_valid, 'errors': abstract_errors},
            'keywords': {'valid': keywords_valid, 'errors': keywords_errors},
            'file': {'valid': file_valid, 'errors': file_errors}
        }

    def estimate_word_count(self):
        """
        Estimate the word count of the abstract text.

        Returns:
            int: Estimated number of words.
        """
        if not self.abstract:
            return 0
        # Split on whitespace and filter out empty strings
        words = [w for w in self.abstract.split() if w.strip()]
        return len(words)

    def estimate_reading_time(self, words_per_minute=200):
        """
        Estimate reading time for the abstract in minutes.

        Args:
            words_per_minute (int): Average reading speed.

        Returns:
            float: Estimated reading time in minutes.
        """
        word_count = self.estimate_word_count()
        return round(word_count / words_per_minute, 2)

    def extract_title_keywords(self):
        """
        Extract potential keywords from the paper title using simple NLP.

        Returns:
            list: List of potential keywords extracted from the title.
        """
        stop_words = {
            'a', 'an', 'the', 'is', 'are', 'was', 'were', 'of', 'in', 'to',
            'for', 'with', 'on', 'at', 'from', 'by', 'and', 'or', 'but',
            'not', 'as', 'using', 'based', 'towards', 'via'
        }
        words = re.findall(r'\b[a-zA-Z]+\b', self.title.lower())
        return [w for w in words if w not in stop_words and len(w) > 2]

    def get_metadata(self):
        """
        Return a summary dictionary of all paper metadata.

        Returns:
            dict: Paper metadata including computed fields.
        """
        return {
            'title': self.title,
            'abstract_preview': self.abstract[:200] + '...' if len(self.abstract) > 200 else self.abstract,
            'authors': self.authors,
            'keywords': self.keywords,
            'file_name': self.file_name,
            'page_count': self.page_count,
            'word_count': self.estimate_word_count(),
            'reading_time_minutes': self.estimate_reading_time(),
            'created_at': self.created_at.isoformat()
        }

    def __repr__(self):
        return f'Paper("{self.title[:50]}", authors={len(self.authors)})'
