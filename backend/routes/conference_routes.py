"""
Conference routes providing full CRUD operations for academic conferences.
Supports creating, reading, updating, and deleting conference records.
"""

from flask import Blueprint, request, jsonify
from models.database import db
from models.conference import Conference

conference_bp = Blueprint('conferences', __name__)


@conference_bp.route('/api/conferences', methods=['GET'])
def get_conferences():
    """
    Retrieve all conferences with optional status filtering.

    Query Parameters:
        status (str): Filter conferences by status (open, closed, archived).

    Returns:
        JSON array of conference objects with 200 status.
    """
    try:
        status_filter = request.args.get('status')
        query = Conference.query

        if status_filter:
            query = query.filter_by(status=status_filter)

        conferences = query.order_by(Conference.created_at.desc()).all()
        return jsonify([c.to_dict() for c in conferences]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@conference_bp.route('/api/conferences/<int:conference_id>', methods=['GET'])
def get_conference(conference_id):
    """
    Retrieve a single conference by its ID.

    Args:
        conference_id (int): Conference primary key.

    Returns:
        JSON conference object with 200, or 404 if not found.
    """
    try:
        conference = Conference.query.get(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404
        return jsonify(conference.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@conference_bp.route('/api/conferences', methods=['POST'])
def create_conference():
    """
    Create a new conference from JSON request body.

    Expected JSON fields:
        name (str): Conference full name (required).
        acronym (str): Short acronym (required).
        submission_deadline (str): Deadline date string (required).
        description, website, location, tracks, topics, etc. (optional).

    Returns:
        JSON conference object with 201 status on success.
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('name') or not data.get('acronym'):
            return jsonify({'error': 'Name and acronym are required'}), 400
        if not data.get('submission_deadline'):
            return jsonify({'error': 'Submission deadline is required'}), 400

        conference = Conference(
            name=data['name'],
            acronym=data['acronym'],
            description=data.get('description', ''),
            website=data.get('website', ''),
            location=data.get('location', ''),
            start_date=data.get('start_date', ''),
            end_date=data.get('end_date', ''),
            submission_deadline=data['submission_deadline'],
            review_deadline=data.get('review_deadline', ''),
            notification_date=data.get('notification_date', ''),
            tracks=data.get('tracks', ''),
            topics=data.get('topics', ''),
            max_papers=data.get('max_papers', 100),
            status=data.get('status', 'open')
        )

        db.session.add(conference)
        db.session.commit()

        return jsonify(conference.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@conference_bp.route('/api/conferences/<int:conference_id>', methods=['PUT'])
def update_conference(conference_id):
    """
    Update an existing conference by its ID.

    Args:
        conference_id (int): Conference primary key.

    Returns:
        JSON updated conference object with 200 status.
    """
    try:
        conference = Conference.query.get(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404

        data = request.get_json()

        # Update only provided fields
        updatable_fields = [
            'name', 'acronym', 'description', 'website', 'location',
            'start_date', 'end_date', 'submission_deadline', 'review_deadline',
            'notification_date', 'tracks', 'topics', 'max_papers', 'status'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(conference, field, data[field])

        db.session.commit()
        return jsonify(conference.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@conference_bp.route('/api/conferences/<int:conference_id>', methods=['DELETE'])
def delete_conference(conference_id):
    """
    Delete a conference by its ID.

    Args:
        conference_id (int): Conference primary key.

    Returns:
        JSON success message with 200 status.
    """
    try:
        conference = Conference.query.get(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404

        db.session.delete(conference)
        db.session.commit()

        return jsonify({'message': f'Conference {conference_id} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@conference_bp.route('/api/conferences/<int:conference_id>/stats', methods=['GET'])
def get_conference_stats(conference_id):
    """
    Get statistics for a specific conference including paper and review counts.

    Args:
        conference_id (int): Conference primary key.

    Returns:
        JSON statistics object with 200 status.
    """
    try:
        conference = Conference.query.get(conference_id)
        if not conference:
            return jsonify({'error': 'Conference not found'}), 404

        papers = conference.papers or []
        total_reviews = sum(len(p.reviews) for p in papers)
        accepted = sum(1 for p in papers if p.status == 'accepted')
        rejected = sum(1 for p in papers if p.status == 'rejected')
        under_review = sum(1 for p in papers if p.status == 'under_review')

        return jsonify({
            'conference_id': conference_id,
            'total_papers': len(papers),
            'total_reviews': total_reviews,
            'accepted': accepted,
            'rejected': rejected,
            'under_review': under_review,
            'pending': len(papers) - accepted - rejected - under_review
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
