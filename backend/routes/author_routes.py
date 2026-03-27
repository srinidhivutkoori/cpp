"""
Author routes providing full CRUD operations for paper authors.
Manages author profiles, affiliations, and expertise information.
"""

from flask import Blueprint, request, jsonify
from models.database import db
from models.author import Author

author_bp = Blueprint('authors', __name__)


@author_bp.route('/api/authors', methods=['GET'])
def get_authors():
    """
    Retrieve all authors with optional filtering by affiliation or country.

    Query Parameters:
        affiliation (str): Filter by institution/organization.
        country (str): Filter by country.

    Returns:
        JSON array of author objects with 200 status.
    """
    try:
        query = Author.query

        affiliation = request.args.get('affiliation')
        if affiliation:
            query = query.filter(Author.affiliation.ilike(f'%{affiliation}%'))

        country = request.args.get('country')
        if country:
            query = query.filter_by(country=country)

        authors = query.order_by(Author.last_name.asc()).all()
        return jsonify([a.to_dict() for a in authors]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@author_bp.route('/api/authors/<int:author_id>', methods=['GET'])
def get_author(author_id):
    """
    Retrieve a single author by their ID.

    Args:
        author_id (int): Author primary key.

    Returns:
        JSON author object with 200, or 404 if not found.
    """
    try:
        author = Author.query.get(author_id)
        if not author:
            return jsonify({'error': 'Author not found'}), 404
        return jsonify(author.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@author_bp.route('/api/authors', methods=['POST'])
def create_author():
    """
    Create a new author profile.

    Expected JSON fields:
        first_name (str): Author's first name (required).
        last_name (str): Author's last name (required).
        email (str): Author's email (required, unique).
        affiliation, department, country, orcid, expertise, bio (optional).

    Returns:
        JSON author object with 201 status on success.
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('first_name') or not data.get('last_name'):
            return jsonify({'error': 'First name and last name are required'}), 400
        if not data.get('email'):
            return jsonify({'error': 'Email is required'}), 400

        # Check for duplicate email
        existing = Author.query.filter_by(email=data['email']).first()
        if existing:
            return jsonify({'error': 'An author with this email already exists'}), 409

        author = Author(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            affiliation=data.get('affiliation', ''),
            department=data.get('department', ''),
            country=data.get('country', ''),
            orcid=data.get('orcid', ''),
            expertise=data.get('expertise', ''),
            bio=data.get('bio', ''),
            h_index=data.get('h_index')
        )

        db.session.add(author)
        db.session.commit()

        return jsonify(author.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@author_bp.route('/api/authors/<int:author_id>', methods=['PUT'])
def update_author(author_id):
    """
    Update an existing author profile.

    Args:
        author_id (int): Author primary key.

    Returns:
        JSON updated author object with 200 status.
    """
    try:
        author = Author.query.get(author_id)
        if not author:
            return jsonify({'error': 'Author not found'}), 404

        data = request.get_json()

        updatable_fields = [
            'first_name', 'last_name', 'email', 'affiliation',
            'department', 'country', 'orcid', 'expertise', 'bio', 'h_index'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(author, field, data[field])

        db.session.commit()
        return jsonify(author.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@author_bp.route('/api/authors/<int:author_id>', methods=['DELETE'])
def delete_author(author_id):
    """
    Delete an author profile by their ID.

    Args:
        author_id (int): Author primary key.

    Returns:
        JSON success message with 200 status.
    """
    try:
        author = Author.query.get(author_id)
        if not author:
            return jsonify({'error': 'Author not found'}), 404

        db.session.delete(author)
        db.session.commit()

        return jsonify({'message': f'Author {author_id} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@author_bp.route('/api/authors/<int:author_id>/papers', methods=['GET'])
def get_author_papers(author_id):
    """
    Retrieve all papers submitted by a specific author.

    Args:
        author_id (int): Author primary key.

    Returns:
        JSON array of paper objects with 200 status.
    """
    try:
        author = Author.query.get(author_id)
        if not author:
            return jsonify({'error': 'Author not found'}), 404

        papers = author.papers or []
        return jsonify([p.to_dict() for p in papers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
