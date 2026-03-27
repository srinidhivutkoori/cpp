"""
Flask application factory for the Academic Conference Paper Submission System.
Student: Srinidhi Vutkoori (X25173243)
Module: Cloud Platform Programming - MSc at NCI

This module creates and configures the Flask application with all services,
routes, and database initialization. Supports both AWS and mock modes.
"""

import os
import sys

# Add parent directory to path so paperflow library can be imported
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask, jsonify
from flask_cors import CORS
from config import config_by_name
from models.database import db, init_db
from routes.conference_routes import conference_bp
from routes.paper_routes import paper_bp
from routes.review_routes import review_bp
from routes.author_routes import author_bp
from routes.aws_routes import aws_bp
from services.dynamodb_service import DynamoDBService
from services.s3_service import S3Service
from services.ses_service import SESService
from services.comprehend_service import ComprehendService
from services.cloudfront_service import CloudFrontService
from services.lambda_service import LambdaService


def create_app(config_name='development'):
    """
    Application factory that creates and configures the Flask application.

    Args:
        config_name (str): Configuration environment name
                          ('development', 'testing', 'production').

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)

    # Load configuration based on environment
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))

    # Enable Cross-Origin Resource Sharing for frontend integration
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Initialize SQLAlchemy database
    init_db(app)

    # Initialize AWS services (mock mode by default)
    use_aws = app.config.get('USE_AWS', False)
    region = app.config.get('AWS_REGION', 'eu-west-1')

    app.config['DYNAMODB_SERVICE'] = DynamoDBService(use_aws=use_aws, region=region)
    app.config['S3_SERVICE'] = S3Service(
        use_aws=use_aws,
        bucket_name=app.config.get('S3_BUCKET_NAME', 'confpaper-uploads'),
        region=region
    )
    app.config['SES_SERVICE'] = SESService(
        use_aws=use_aws,
        sender_email=app.config.get('SES_SENDER_EMAIL', 'noreply@confpaper.example.com'),
        region=region
    )
    app.config['COMPREHEND_SERVICE'] = ComprehendService(use_aws=use_aws, region=region)
    app.config['CLOUDFRONT_SERVICE'] = CloudFrontService(
        use_aws=use_aws,
        domain_name=app.config.get('CLOUDFRONT_DOMAIN', 'd123456789.cloudfront.net'),
        distribution_id=app.config.get('CLOUDFRONT_DISTRIBUTION_ID', ''),
        region=region
    )
    app.config['LAMBDA_SERVICE'] = LambdaService(
        use_aws=use_aws,
        function_prefix=app.config.get('LAMBDA_FUNCTION_PREFIX', 'confpaper_'),
        region=region
    )

    # Register route blueprints
    app.register_blueprint(conference_bp)
    app.register_blueprint(paper_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(author_bp)
    app.register_blueprint(aws_bp)

    # Root endpoint with application information
    @app.route('/')
    def index():
        """Root endpoint returning application metadata."""
        return jsonify({
            'application': 'Academic Conference Paper Submission System',
            'student': 'Srinidhi Vutkoori',
            'student_id': 'X25173243',
            'version': '1.0.0',
            'aws_mode': 'live' if use_aws else 'mock',
            'endpoints': {
                'conferences': '/api/conferences',
                'papers': '/api/papers',
                'reviews': '/api/reviews',
                'authors': '/api/authors',
                'aws_status': '/api/aws/status'
            }
        })

    # Health check endpoint
    @app.route('/api/health')
    def health():
        """Health check endpoint for monitoring."""
        return jsonify({'status': 'healthy', 'mode': 'aws' if use_aws else 'mock'}), 200

    # Dashboard statistics endpoint
    @app.route('/api/dashboard')
    def dashboard():
        """Dashboard endpoint with system-wide statistics."""
        from models.conference import Conference
        from models.paper import Paper
        from models.review import Review
        from models.author import Author

        try:
            return jsonify({
                'total_conferences': Conference.query.count(),
                'total_papers': Paper.query.count(),
                'total_reviews': Review.query.count(),
                'total_authors': Author.query.count(),
                'papers_by_status': {
                    'submitted': Paper.query.filter_by(status='submitted').count(),
                    'under_review': Paper.query.filter_by(status='under_review').count(),
                    'accepted': Paper.query.filter_by(status='accepted').count(),
                    'rejected': Paper.query.filter_by(status='rejected').count()
                },
                'reviews_by_status': {
                    'assigned': Review.query.filter_by(status='assigned').count(),
                    'in_progress': Review.query.filter_by(status='in_progress').count(),
                    'completed': Review.query.filter_by(status='completed').count()
                }
            }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app


# Run the application when executed directly
if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development')
    app = create_app(env)
    app.run(host='0.0.0.0', port=5000, debug=True)
