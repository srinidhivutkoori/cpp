# PaperFlow

Academic Conference Paper Management Library for the Cloud Platform Programming project.

## Overview

PaperFlow is a Python library that provides tools for managing academic conference paper submissions, peer reviews, and acceptance decisions. It implements core domain logic for paper validation, reviewer assignment optimization, conference management, submission workflow tracking, and review score aggregation.

## Installation

```bash
pip install -e .
```

## Classes

- **Paper**: Validates paper metadata, checks format, estimates word count
- **Reviewer**: Expertise matching, conflict detection, assignment optimization
- **Conference**: Deadline management, track organization, capacity planning
- **Submission**: Workflow state machine (submitted -> under_review -> accepted/rejected)
- **Scoring**: Weighted review aggregation, statistical analysis, threshold-based decisions

## Usage

```python
from paperflow import Paper, Reviewer, Scoring

# Validate a paper
paper = Paper("My Research Paper", "This is the abstract...", keywords=["AI", "cloud", "NLP"])
report = paper.validate_all()

# Match reviewer expertise
reviewer = Reviewer("Dr. Smith", "smith@uni.edu", expertise_areas=["AI", "cloud"])
score = reviewer.calculate_expertise_match(["AI", "machine learning"])

# Aggregate review scores
scoring = Scoring()
scoring.add_review({"originality_score": 8, "significance_score": 7, "clarity_score": 9, "methodology_score": 8, "overall_score": 8})
recommendation = scoring.generate_recommendation()
```

## Testing

```bash
pytest tests/ -v
```

## Author

Srinidhi Vutkoori (X25173243) - National College of Ireland
