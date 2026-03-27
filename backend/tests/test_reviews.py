"""
Test suite for review CRUD operations.
Tests all REST endpoints for creating, reading, updating, and deleting reviews.
"""

import json
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from models.database import db


@pytest.fixture
def client():
    """Create a test client with an in-memory SQLite database."""
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()


@pytest.fixture
def setup_data(client):
    """Create prerequisite records for review tests."""
    author_resp = client.post('/api/authors', data=json.dumps({
        'first_name': 'John', 'last_name': 'Doe', 'email': 'john@test.edu'
    }), content_type='application/json')
    author_id = author_resp.get_json()['id']

    conf_resp = client.post('/api/conferences', data=json.dumps({
        'name': 'Test Conf', 'acronym': 'TC', 'submission_deadline': '2026-06-01'
    }), content_type='application/json')
    conf_id = conf_resp.get_json()['id']

    paper_resp = client.post('/api/papers', data=json.dumps({
        'title': 'Test Paper', 'abstract': 'This is a test abstract for NLP analysis.',
        'conference_id': conf_id, 'author_id': author_id
    }), content_type='application/json')
    paper_id = paper_resp.get_json()['id']

    return {'paper_id': paper_id, 'author_id': author_id, 'conference_id': conf_id}


@pytest.fixture
def sample_review(setup_data):
    """Return sample review data with a valid paper ID."""
    return {
        'reviewer_name': 'Dr. Alice Reviewer',
        'reviewer_email': 'alice@review.edu',
        'reviewer_expertise': 'Cloud Computing',
        'paper_id': setup_data['paper_id'],
        'originality_score': 8,
        'significance_score': 7,
        'clarity_score': 9,
        'methodology_score': 8,
        'overall_score': 8,
        'summary_comment': 'Well-written paper with solid methodology.',
        'strengths': 'Novel approach, clear presentation',
        'weaknesses': 'Limited evaluation scope',
        'recommendation': 'accept',
        'confidence': 4
    }


def test_create_review(client, sample_review):
    """Test creating a new review assignment."""
    response = client.post(
        '/api/reviews',
        data=json.dumps(sample_review),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['reviewer_name'] == 'Dr. Alice Reviewer'
    assert data['status'] == 'assigned'


def test_create_review_missing_fields(client, setup_data):
    """Test that creating a review without required fields fails."""
    response = client.post(
        '/api/reviews',
        data=json.dumps({'paper_id': setup_data['paper_id']}),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_get_all_reviews(client, sample_review):
    """Test retrieving all reviews."""
    client.post('/api/reviews', data=json.dumps(sample_review),
                content_type='application/json')
    response = client.get('/api/reviews')
    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_get_review_by_id(client, sample_review):
    """Test retrieving a single review by its ID."""
    create_resp = client.post('/api/reviews', data=json.dumps(sample_review),
                              content_type='application/json')
    review_id = create_resp.get_json()['id']
    response = client.get(f'/api/reviews/{review_id}')
    assert response.status_code == 200
    assert response.get_json()['reviewer_email'] == 'alice@review.edu'


def test_get_review_not_found(client):
    """Test that requesting a non-existent review returns 404."""
    response = client.get('/api/reviews/9999')
    assert response.status_code == 404


def test_update_review_scores(client, sample_review):
    """Test updating review scores and completion."""
    create_resp = client.post('/api/reviews', data=json.dumps(sample_review),
                              content_type='application/json')
    review_id = create_resp.get_json()['id']

    update_data = {
        'overall_score': 9,
        'recommendation': 'strong_accept',
        'detailed_comments': 'Excellent work overall.'
    }
    response = client.put(
        f'/api/reviews/{review_id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['overall_score'] == 9
    assert data['recommendation'] == 'strong_accept'


def test_delete_review(client, sample_review):
    """Test deleting a review."""
    create_resp = client.post('/api/reviews', data=json.dumps(sample_review),
                              content_type='application/json')
    review_id = create_resp.get_json()['id']

    response = client.delete(f'/api/reviews/{review_id}')
    assert response.status_code == 200

    get_resp = client.get(f'/api/reviews/{review_id}')
    assert get_resp.status_code == 404


def test_delete_review_not_found(client):
    """Test that deleting a non-existent review returns 404."""
    response = client.delete('/api/reviews/9999')
    assert response.status_code == 404


def test_filter_reviews_by_paper(client, sample_review):
    """Test filtering reviews by paper_id query parameter."""
    client.post('/api/reviews', data=json.dumps(sample_review),
                content_type='application/json')
    paper_id = sample_review['paper_id']

    response = client.get(f'/api/reviews?paper_id={paper_id}')
    assert response.status_code == 200
    assert len(response.get_json()) == 1
