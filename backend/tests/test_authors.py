"""
Test suite for author CRUD operations.
Tests all REST endpoints for creating, reading, updating, and deleting authors.
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
def sample_author():
    """Return sample author data for testing."""
    return {
        'first_name': 'Maria',
        'last_name': 'Garcia',
        'email': 'maria.garcia@university.edu',
        'affiliation': 'National College of Ireland',
        'department': 'School of Computing',
        'country': 'Ireland',
        'orcid': '0000-0002-1234-5678',
        'expertise': 'cloud computing, machine learning, NLP',
        'bio': 'Associate Professor in Computing',
        'h_index': 15
    }


def test_create_author(client, sample_author):
    """Test creating a new author with valid data."""
    response = client.post(
        '/api/authors',
        data=json.dumps(sample_author),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['first_name'] == 'Maria'
    assert data['email'] == 'maria.garcia@university.edu'


def test_create_author_missing_name(client):
    """Test that creating an author without a name fails with 400."""
    response = client.post(
        '/api/authors',
        data=json.dumps({'email': 'test@test.com'}),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_create_author_missing_email(client):
    """Test that creating an author without an email fails with 400."""
    response = client.post(
        '/api/authors',
        data=json.dumps({'first_name': 'Test', 'last_name': 'User'}),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_create_author_duplicate_email(client, sample_author):
    """Test that creating an author with a duplicate email returns 409."""
    client.post('/api/authors', data=json.dumps(sample_author),
                content_type='application/json')
    response = client.post('/api/authors', data=json.dumps(sample_author),
                           content_type='application/json')
    assert response.status_code == 409


def test_get_all_authors(client, sample_author):
    """Test retrieving all authors returns a list."""
    client.post('/api/authors', data=json.dumps(sample_author),
                content_type='application/json')
    response = client.get('/api/authors')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_author_by_id(client, sample_author):
    """Test retrieving a single author by their ID."""
    create_resp = client.post('/api/authors', data=json.dumps(sample_author),
                              content_type='application/json')
    author_id = create_resp.get_json()['id']
    response = client.get(f'/api/authors/{author_id}')
    assert response.status_code == 200
    assert response.get_json()['last_name'] == 'Garcia'


def test_get_author_not_found(client):
    """Test that requesting a non-existent author returns 404."""
    response = client.get('/api/authors/9999')
    assert response.status_code == 404


def test_update_author(client, sample_author):
    """Test updating author fields."""
    create_resp = client.post('/api/authors', data=json.dumps(sample_author),
                              content_type='application/json')
    author_id = create_resp.get_json()['id']

    update_data = {'affiliation': 'MIT', 'h_index': 25}
    response = client.put(
        f'/api/authors/{author_id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['affiliation'] == 'MIT'
    assert data['h_index'] == 25


def test_update_author_not_found(client):
    """Test that updating a non-existent author returns 404."""
    response = client.put(
        '/api/authors/9999',
        data=json.dumps({'first_name': 'Test'}),
        content_type='application/json'
    )
    assert response.status_code == 404


def test_delete_author(client, sample_author):
    """Test deleting an author."""
    create_resp = client.post('/api/authors', data=json.dumps(sample_author),
                              content_type='application/json')
    author_id = create_resp.get_json()['id']

    response = client.delete(f'/api/authors/{author_id}')
    assert response.status_code == 200

    get_resp = client.get(f'/api/authors/{author_id}')
    assert get_resp.status_code == 404


def test_delete_author_not_found(client):
    """Test that deleting a non-existent author returns 404."""
    response = client.delete('/api/authors/9999')
    assert response.status_code == 404
