"""
Test suite for conference CRUD operations.
Tests all REST endpoints for creating, reading, updating, and deleting conferences.
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
def sample_conference():
    """Return sample conference data for testing."""
    return {
        'name': 'International Conference on Software Engineering',
        'acronym': 'ICSE',
        'description': 'Premier software engineering conference',
        'website': 'https://icse2026.org',
        'location': 'Dublin, Ireland',
        'start_date': '2026-06-15',
        'end_date': '2026-06-20',
        'submission_deadline': '2026-03-01',
        'review_deadline': '2026-04-15',
        'notification_date': '2026-05-01',
        'tracks': 'Technical Track, Industry Track',
        'topics': 'software engineering, testing, AI',
        'max_papers': 200,
        'status': 'open'
    }


def test_create_conference(client, sample_conference):
    """Test creating a new conference with valid data."""
    response = client.post(
        '/api/conferences',
        data=json.dumps(sample_conference),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == sample_conference['name']
    assert data['acronym'] == 'ICSE'
    assert data['id'] is not None


def test_create_conference_missing_name(client):
    """Test that creating a conference without a name fails with 400."""
    response = client.post(
        '/api/conferences',
        data=json.dumps({'acronym': 'TEST', 'submission_deadline': '2026-03-01'}),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_create_conference_missing_deadline(client):
    """Test that creating a conference without a deadline fails with 400."""
    response = client.post(
        '/api/conferences',
        data=json.dumps({'name': 'Test Conf', 'acronym': 'TC'}),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_get_all_conferences(client, sample_conference):
    """Test retrieving all conferences returns a list."""
    client.post('/api/conferences', data=json.dumps(sample_conference),
                content_type='application/json')
    response = client.get('/api/conferences')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_conference_by_id(client, sample_conference):
    """Test retrieving a single conference by its ID."""
    create_resp = client.post('/api/conferences', data=json.dumps(sample_conference),
                              content_type='application/json')
    conf_id = create_resp.get_json()['id']
    response = client.get(f'/api/conferences/{conf_id}')
    assert response.status_code == 200
    assert response.get_json()['acronym'] == 'ICSE'


def test_get_conference_not_found(client):
    """Test that requesting a non-existent conference returns 404."""
    response = client.get('/api/conferences/9999')
    assert response.status_code == 404


def test_update_conference(client, sample_conference):
    """Test updating conference fields."""
    create_resp = client.post('/api/conferences', data=json.dumps(sample_conference),
                              content_type='application/json')
    conf_id = create_resp.get_json()['id']

    update_data = {'name': 'Updated Conference Name', 'status': 'closed'}
    response = client.put(
        f'/api/conferences/{conf_id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Updated Conference Name'
    assert data['status'] == 'closed'


def test_update_conference_not_found(client):
    """Test that updating a non-existent conference returns 404."""
    response = client.put(
        '/api/conferences/9999',
        data=json.dumps({'name': 'Test'}),
        content_type='application/json'
    )
    assert response.status_code == 404


def test_delete_conference(client, sample_conference):
    """Test deleting a conference."""
    create_resp = client.post('/api/conferences', data=json.dumps(sample_conference),
                              content_type='application/json')
    conf_id = create_resp.get_json()['id']

    response = client.delete(f'/api/conferences/{conf_id}')
    assert response.status_code == 200

    # Verify it is deleted
    get_resp = client.get(f'/api/conferences/{conf_id}')
    assert get_resp.status_code == 404


def test_delete_conference_not_found(client):
    """Test that deleting a non-existent conference returns 404."""
    response = client.delete('/api/conferences/9999')
    assert response.status_code == 404


def test_get_conferences_filter_by_status(client, sample_conference):
    """Test filtering conferences by status query parameter."""
    client.post('/api/conferences', data=json.dumps(sample_conference),
                content_type='application/json')

    response = client.get('/api/conferences?status=open')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1

    response = client.get('/api/conferences?status=closed')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 0
