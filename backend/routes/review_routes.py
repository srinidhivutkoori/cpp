"""
Review routes providing full CRUD operations with scoring functionality.
Supports reviewer assignment, score submission, and aggregation.
"""

from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from models.database import db
from models.review import Review

review_bp = Blueprint('reviews', __name__)


@review_bp.route('/api/reviews', methods=['GET'])
def get_reviews():
    """
    Retrieve all reviews with optional filtering by paper or status.

    Query Parameters:
        paper_id (int): Filter reviews by paper.
        status (str): Filter by review status.
        reviewer_email (str): Filter by reviewer email.

    Returns:
        JSON array of review objects with 200 status.
    """
    try:
        query = Review.query

        paper_id = request.args.get('paper_id')
        if paper_id:
            query = query.filter_by(paper_id=int(paper_id))

        status_filter = request.args.get('status')
        if status_filter:
            query = query.filter_by(status=status_filter)

        reviewer_email = request.args.get('reviewer_email')
        if reviewer_email:
            query = query.filter_by(reviewer_email=reviewer_email)

        reviews = query.order_by(Review.assigned_at.desc()).all()
        return jsonify([r.to_dict() for r in reviews]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@review_bp.route('/api/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """
    Retrieve a single review by its ID.

    Args:
        review_id (int): Review primary key.

    Returns:
        JSON review object with 200, or 404 if not found.
    """
    try:
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'error': 'Review not found'}), 404
        return jsonify(review.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@review_bp.route('/api/reviews', methods=['POST'])
def create_review():
    """
    Create a new review assignment for a paper.
    Sends email notification to the assigned reviewer via SES.

    Returns:
        JSON review object with 201 status on success.
    """
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('reviewer_name') or not data.get('reviewer_email'):
            return jsonify({'error': 'Reviewer name and email are required'}), 400
        if not data.get('paper_id'):
            return jsonify({'error': 'Paper ID is required'}), 400

        review = Review(
            reviewer_name=data['reviewer_name'],
            reviewer_email=data['reviewer_email'],
            reviewer_expertise=data.get('reviewer_expertise', ''),
            paper_id=int(data['paper_id']),
            status='assigned',
            originality_score=data.get('originality_score'),
            significance_score=data.get('significance_score'),
            clarity_score=data.get('clarity_score'),
            methodology_score=data.get('methodology_score'),
            overall_score=data.get('overall_score'),
            summary_comment=data.get('summary_comment', ''),
            strengths=data.get('strengths', ''),
            weaknesses=data.get('weaknesses', ''),
            detailed_comments=data.get('detailed_comments', ''),
            confidential_comments=data.get('confidential_comments', ''),
            recommendation=data.get('recommendation', ''),
            confidence=data.get('confidence')
        )

        db.session.add(review)
        db.session.commit()

        # Send review assignment notification via SES
        ses_service = current_app.config.get('SES_SERVICE')
        if ses_service and review.paper:
            ses_service.send_review_assignment(
                review.reviewer_email,
                review.reviewer_name,
                review.paper.title,
                review.paper.conference.review_deadline if review.paper.conference else 'TBD'
            )

        return jsonify(review.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@review_bp.route('/api/reviews/<int:review_id>', methods=['PUT'])
def update_review(review_id):
    """
    Update an existing review with scores and comments.

    Args:
        review_id (int): Review primary key.

    Returns:
        JSON updated review object with 200 status.
    """
    try:
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'error': 'Review not found'}), 404

        data = request.get_json()

        updatable_fields = [
            'reviewer_name', 'reviewer_email', 'reviewer_expertise',
            'originality_score', 'significance_score', 'clarity_score',
            'methodology_score', 'overall_score', 'summary_comment',
            'strengths', 'weaknesses', 'detailed_comments',
            'confidential_comments', 'recommendation', 'confidence', 'status'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(review, field, data[field])

        # Mark as completed if all scores are provided
        if all([review.originality_score, review.significance_score,
                review.clarity_score, review.methodology_score,
                review.overall_score, review.recommendation]):
            review.status = 'completed'
            review.completed_at = datetime.utcnow()

        db.session.commit()
        return jsonify(review.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@review_bp.route('/api/reviews/<int:review_id>', methods=['DELETE'])
def delete_review(review_id):
    """
    Delete a review by its ID.

    Args:
        review_id (int): Review primary key.

    Returns:
        JSON success message with 200 status.
    """
    try:
        review = Review.query.get(review_id)
        if not review:
            return jsonify({'error': 'Review not found'}), 404

        db.session.delete(review)
        db.session.commit()

        return jsonify({'message': f'Review {review_id} deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@review_bp.route('/api/papers/<int:paper_id>/reviews', methods=['GET'])
def get_paper_reviews(paper_id):
    """
    Retrieve all reviews for a specific paper.

    Args:
        paper_id (int): Paper primary key.

    Returns:
        JSON array of review objects with 200 status.
    """
    try:
        reviews = Review.query.filter_by(paper_id=paper_id).order_by(Review.assigned_at.desc()).all()
        return jsonify([r.to_dict() for r in reviews]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@review_bp.route('/api/papers/<int:paper_id>/reviews', methods=['POST'])
def create_paper_review(paper_id):
    """
    Submit a review for a specific paper.
    Accepts the simplified review form from the frontend (score, recommendation, comments)
    and maps it to the full review model.

    Args:
        paper_id (int): Paper primary key.

    Returns:
        JSON review object with 201 status on success.
    """
    try:
        data = request.get_json()

        # Build reviewer info from auth context or request data
        reviewer_name = data.get('reviewer_name', 'Anonymous Reviewer')
        reviewer_email = data.get('reviewer_email', 'reviewer@paperhub.com')

        review = Review(
            reviewer_name=reviewer_name,
            reviewer_email=reviewer_email,
            paper_id=paper_id,
            overall_score=data.get('score'),
            originality_score=data.get('score'),
            significance_score=data.get('score'),
            clarity_score=data.get('score'),
            methodology_score=data.get('score'),
            recommendation=data.get('recommendation', ''),
            detailed_comments=data.get('comments', ''),
            summary_comment=data.get('comments', ''),
            status='completed',
            completed_at=datetime.utcnow()
        )

        db.session.add(review)
        db.session.commit()

        return jsonify(review.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@review_bp.route('/api/papers/<int:paper_id>/reviews/aggregate', methods=['GET'])
def aggregate_reviews(paper_id):
    """
    Calculate aggregated review scores for a paper.
    Provides average scores across all completed reviews.

    Args:
        paper_id (int): Paper primary key.

    Returns:
        JSON aggregation results with 200 status.
    """
    try:
        reviews = Review.query.filter_by(paper_id=paper_id, status='completed').all()

        if not reviews:
            return jsonify({
                'paper_id': paper_id,
                'total_reviews': 0,
                'message': 'No completed reviews found'
            }), 200

        count = len(reviews)
        avg_originality = sum(r.originality_score or 0 for r in reviews) / count
        avg_significance = sum(r.significance_score or 0 for r in reviews) / count
        avg_clarity = sum(r.clarity_score or 0 for r in reviews) / count
        avg_methodology = sum(r.methodology_score or 0 for r in reviews) / count
        avg_overall = sum(r.overall_score or 0 for r in reviews) / count

        # Count recommendations
        recommendations = {}
        for r in reviews:
            rec = r.recommendation or 'unknown'
            recommendations[rec] = recommendations.get(rec, 0) + 1

        return jsonify({
            'paper_id': paper_id,
            'total_reviews': count,
            'average_scores': {
                'originality': round(avg_originality, 2),
                'significance': round(avg_significance, 2),
                'clarity': round(avg_clarity, 2),
                'methodology': round(avg_methodology, 2),
                'overall': round(avg_overall, 2)
            },
            'recommendations': recommendations
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
