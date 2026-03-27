"""
Test suite for paper CRUD operations.
Tests all REST endpoints for creating, reading, updating, and deleting papers.
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
    """Create prerequisite conference and author for paper tests."""
    # Create an author first
    author_data = {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'jane.smith@test.edu'
    }
    author_resp = client.post('/api/authors', data=json.dumps(author_data),
                              content_type='application/json')
    author_id = author_resp.get_json()['id']

    # Create a conference
    conf_data = {
        'name': 'Test Conference',
        'acronym': 'TC2026',
        'submission_deadline': '2026-06-01'
    }
    conf_resp = client.post('/api/conferences', data=json.dumps(conf_data),
                            content_type='application/json')
    conf_id = conf_resp.get_json()['id']

    return {'author_id': author_id, 'conference_id': conf_id}


@pytest.fixture
def sample_paper(setup_data):
    """Return sample paper data with valid foreign keys."""
    return {
        'title': 'A Novel Approach to Cloud Computing Optimization',
        'abstract': 'This paper presents a novel approach to optimizing cloud computing '
                    'resources using machine learning techniques. We demonstrate significant '
                    'improvements in resource utilization and cost reduction.',
        'keywords': 'cloud computing, optimization, machine learning',
        'track': 'Technical Track',
        'conference_id': setup_data['conference_id'],
        'author_id': setup_data['author_id']
    }


def test_create_paper(client, sample_paper):
    """Test creating a new paper with valid data."""
    response = client.post(
        '/api/papers',
        data=json.dumps(sample_paper),
        content_type='application/json'
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == sample_paper['title']
    assert data['status'] == 'submitted'


def test_create_paper_missing_title(client, setup_data):
    """Test that creating a paper without a title fails with 400."""
    response = client.post(
        '/api/papers',
        data=json.dumps({
            'abstract': 'Test abstract',
            'conference_id': setup_data['conference_id'],
            'author_id': setup_data['author_id']
        }),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_create_paper_missing_ids(client):
    """Test that creating a paper without conference and author IDs fails."""
    response = client.post(
        '/api/papers',
        data=json.dumps({'title': 'Test', 'abstract': 'Test'}),
        content_type='application/json'
    )
    assert response.status_code == 400


def test_get_all_papers(client, sample_paper):
    """Test retrieving all papers returns a list."""
    client.post('/api/papers', data=json.dumps(sample_paper),
                content_type='application/json')
    response = client.get('/api/papers')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 1


def test_get_paper_by_id(client, sample_paper):
    """Test retrieving a single paper by its ID."""
    create_resp = client.post('/api/papers', data=json.dumps(sample_paper),
                              content_type='application/json')
    paper_id = create_resp.get_json()['id']
    response = client.get(f'/api/papers/{paper_id}')
    assert response.status_code == 200
    assert response.get_json()['title'] == sample_paper['title']


def test_get_paper_not_found(client):
    """Test that requesting a non-existent paper returns 404."""
    response = client.get('/api/papers/9999')
    assert response.status_code == 404


def test_update_paper(client, sample_paper):
    """Test updating paper fields including status."""
    create_resp = client.post('/api/papers', data=json.dumps(sample_paper),
                              content_type='application/json')
    paper_id = create_resp.get_json()['id']

    update_data = {'title': 'Updated Title', 'status': 'under_review'}
    response = client.put(
        f'/api/papers/{paper_id}',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Updated Title'
    assert data['status'] == 'under_review'


def test_delete_paper(client, sample_paper):
    """Test deleting a paper."""
    create_resp = client.post('/api/papers', data=json.dumps(sample_paper),
                              content_type='application/json')
    paper_id = create_resp.get_json()['id']

    response = client.delete(f'/api/papers/{paper_id}')
    assert response.status_code == 200

    get_resp = client.get(f'/api/papers/{paper_id}')
    assert get_resp.status_code == 404


def test_filter_papers_by_conference(client, sample_paper):
    """Test filtering papers by conference_id query parameter."""
    client.post('/api/papers', data=json.dumps(sample_paper),
                content_type='application/json')
    conf_id = sample_paper['conference_id']

    response = client.get(f'/api/papers?conference_id={conf_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1


def test_filter_papers_by_status(client, sample_paper):
    """Test filtering papers by status query parameter."""
    client.post('/api/papers', data=json.dumps(sample_paper),
                content_type='application/json')

    response = client.get('/api/papers?status=submitted')
    assert response.status_code == 200
    assert len(response.get_json()) == 1

    response = client.get('/api/papers?status=accepted')
    assert response.status_code == 200
    assert len(response.get_json()) == 0
