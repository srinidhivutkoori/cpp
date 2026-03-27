"""
Paper routes providing full CRUD operations with file upload support.
Integrates with S3 for PDF storage and Comprehend for NLP analysis.
"""

import json
from flask import Blueprint, request, jsonify, current_app
from models.database import db
from models.paper import Paper

paper_bp = Blueprint('papers', __name__)


@paper_bp.route('/api/papers', methods=['GET'])
def get_papers():
    """
    Retrieve all papers with optional filtering by conference or status.

    Query Parameters:
        conference_id (int): Filter by conference.
        status (str): Filter by status.
        author_id (int): Filter by author.

    Returns:
        JSON array of paper objects with 200 status.
    """
    try:
        query = Paper.query

        conference_id = request.args.get('conference_id')
        if conference_id:
            query = query.filter_by(conference_id=int(conference_id))

        status_filter = request.args.get('status')
        if status_filter:
            query = query.filter_by(status=status_filter)

        author_id = request.args.get('author_id')
        if author_id:
            query = query.filter_by(author_id=int(author_id))

        papers = query.order_by(Paper.submitted_at.desc()).all()
        return jsonify([p.to_dict() for p in papers]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@paper_bp.route('/api/papers/<int:paper_id>', methods=['GET'])
def get_paper(paper_id):
    """
    Retrieve a single paper by its ID.

    Args:
        paper_id (int): Paper primary key.

    Returns:
        JSON paper object with 200, or 404 if not found.
    """
    try:
        paper = Paper.query.get(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404
        return jsonify(paper.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@paper_bp.route('/api/papers', methods=['POST'])
def create_paper():
    """
    Create a new paper submission. Handles both JSON and multipart form data
    (for file uploads). Triggers NLP analysis on the abstract.

    Returns:
        JSON paper object with 201 status on success.
    """
    try:
        # Handle both JSON and form data submissions
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            file = request.files.get('file')
        else:
            data = request.get_json()
            file = None

        # Validate required fields
        if not data.get('title') or not data.get('abstract'):
            return jsonify({'error': 'Title and abstract are required'}), 400
        if not data.get('conference_id') or not data.get('author_id'):
            return jsonify({'error': 'Conference ID and Author ID are required'}), 400

        paper = Paper(
            title=data['title'],
            abstract=data['abstract'],
            keywords=data.get('keywords', ''),
            track=data.get('track', ''),
            conference_id=int(data['conference_id']),
            author_id=int(data['author_id']),
            status='submitted',
            word_count=len(data['abstract'].split()),
            page_count=data.get('page_count')
        )

        # Handle file upload through S3 service
        if file and file.filename:
            s3_service = current_app.config.get('S3_SERVICE')
            if s3_service:
                upload_result = s3_service.upload_file(
                    file, file.filename, 'application/pdf'
                )
                paper.file_key = upload_result['file_key']
                paper.file_name = upload_result['file_name']

        # Run NLP analysis on abstract
        comprehend_service = current_app.config.get('COMPREHEND_SERVICE')
        if comprehend_service:
            analysis = comprehend_service.analyze_abstract(data['abstract'])
            paper.nlp_keywords = json.dumps(analysis.get('key_phrases', []))
            paper.nlp_sentiment = analysis.get('sentiment', {}).get('sentiment', 'UNKNOWN')
            paper.nlp_entities = json.dumps(analysis.get('entities', []))

        # Trigger async processing via Lambda
        lambda_service = current_app.config.get('LAMBDA_SERVICE')
        if lambda_service:
            lambda_service.process_paper_submission(paper.id, data['abstract'])

        db.session.add(paper)
        db.session.commit()

        # Send confirmation email via SES
        ses_service = current_app.config.get('SES_SERVICE')
        if ses_service and paper.author:
            ses_service.send_submission_confirmation(
                paper.author.email,
                paper.author.full_name,
                paper.title,
                paper.conference.name if paper.conference else 'Unknown Conference'
            )

        return jsonify(paper.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@paper_bp.route('/api/papers/<int:paper_id>', methods=['PUT'])
def update_paper(paper_id):
    """
    Update an existing paper by its ID.

    Args:
        paper_id (int): Paper primary key.

    Returns:
        JSON updated paper object with 200 status.
    """
    try:
        paper = Paper.query.get(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404

        data = request.get_json()

        updatable_fields = [
            'title', 'abstract', 'keywords', 'track', 'status',
            'decision_notes', 'page_count', 'word_count'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(paper, field, data[field])

        # Re-run NLP analysis if abstract was updated
        if 'abstract' in data:
            comprehend_service = current_app.config.get('COMPREHEND_SERVICE')
            if comprehend_service:
                analysis = comprehend_service.analyze_abstract(data['abstract'])
                paper.nlp_keywords = json.dumps(analysis.get('key_phrases', []))
                paper.nlp_sentiment = analysis.get('sentiment', {}).get('sentiment', 'UNKNOWN')
                paper.nlp_entities = json.dumps(analysis.get('entities', []))

        db.session.commit()
        return jsonify(paper.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@paper_bp.route('/api/papers/<int:paper_id>', methods=['DELETE'])
def delete_paper(paper_id):
    """
    Delete a paper and its associated file from S3.

    Args:
        paper_id (int): Paper primary key.

    Returns:
        JSON success message with 200 status.
    """
    try:
        paper = Paper.query.get(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404

        # Delete associated file from S3
        if paper.file_key:
            s3_service = current_app.config.get('S3_SERVICE')
            if s3_service:
                s3_service.delete_file(paper.file_key)

        db.session.delete(paper)
        db.session.commit()

        return jsonify({'message': f'Paper {paper_id} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@paper_bp.route('/api/papers/<int:paper_id>/analyze', methods=['POST'])
def analyze_paper(paper_id):
    """
    Trigger NLP analysis on a paper's abstract using Amazon Comprehend.

    Args:
        paper_id (int): Paper primary key.

    Returns:
        JSON analysis results with 200 status.
    """
    try:
        paper = Paper.query.get(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404

        comprehend_service = current_app.config.get('COMPREHEND_SERVICE')
        if not comprehend_service:
            return jsonify({'error': 'Comprehend service not available'}), 503

        analysis = comprehend_service.analyze_abstract(paper.abstract)

        # Store analysis results in the paper record
        paper.nlp_keywords = json.dumps(analysis.get('key_phrases', []))
        paper.nlp_sentiment = analysis.get('sentiment', {}).get('sentiment', 'UNKNOWN')
        paper.nlp_entities = json.dumps(analysis.get('entities', []))
        db.session.commit()

        return jsonify({
            'paper_id': paper_id,
            'analysis': analysis
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@paper_bp.route('/api/papers/<int:paper_id>/download', methods=['GET'])
def get_download_url(paper_id):
    """
    Get a CDN-backed download URL for a paper's PDF file.

    Args:
        paper_id (int): Paper primary key.

    Returns:
        JSON with download URL.
    """
    try:
        paper = Paper.query.get(paper_id)
        if not paper:
            return jsonify({'error': 'Paper not found'}), 404

        if not paper.file_key:
            return jsonify({'error': 'No file uploaded for this paper'}), 404

        cloudfront_service = current_app.config.get('CLOUDFRONT_SERVICE')
        if cloudfront_service:
            result = cloudfront_service.get_paper_download_url(paper.file_key)
            return jsonify(result), 200
        else:
            s3_service = current_app.config.get('S3_SERVICE')
            if s3_service:
                url = s3_service.get_file_url(paper.file_key)
                return jsonify({'download_url': url}), 200

        return jsonify({'error': 'No download service available'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500
