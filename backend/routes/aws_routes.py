"""
AWS service status routes for monitoring cloud service connectivity.
Provides health check endpoints for all six AWS services.
"""

from flask import Blueprint, jsonify, current_app

aws_bp = Blueprint('aws', __name__)


@aws_bp.route('/api/aws/status', methods=['GET'])
def get_all_services_status():
    """
    Get the status of all AWS services used by the application.

    Returns:
        JSON object with status for each service.
    """
    try:
        services = {}

        dynamodb = current_app.config.get('DYNAMODB_SERVICE')
        if dynamodb:
            services['dynamodb'] = dynamodb.get_status()

        s3 = current_app.config.get('S3_SERVICE')
        if s3:
            services['s3'] = s3.get_status()

        ses = current_app.config.get('SES_SERVICE')
        if ses:
            services['ses'] = ses.get_status()

        comprehend = current_app.config.get('COMPREHEND_SERVICE')
        if comprehend:
            services['comprehend'] = comprehend.get_status()

        cloudfront = current_app.config.get('CLOUDFRONT_SERVICE')
        if cloudfront:
            services['cloudfront'] = cloudfront.get_status()

        lambda_svc = current_app.config.get('LAMBDA_SERVICE')
        if lambda_svc:
            services['lambda'] = lambda_svc.get_status()

        # Overall status summary
        all_running = all(
            s.get('status') in ('running', 'connected')
            for s in services.values()
        )

        return jsonify({
            'overall_status': 'healthy' if all_running else 'degraded',
            'use_aws': current_app.config.get('USE_AWS', False),
            'services': services
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/dynamodb/status', methods=['GET'])
def dynamodb_status():
    """Check DynamoDB service status."""
    try:
        service = current_app.config.get('DYNAMODB_SERVICE')
        if service:
            return jsonify(service.get_status()), 200
        return jsonify({'error': 'DynamoDB service not initialized'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/s3/status', methods=['GET'])
def s3_status():
    """Check S3 service status."""
    try:
        service = current_app.config.get('S3_SERVICE')
        if service:
            return jsonify(service.get_status()), 200
        return jsonify({'error': 'S3 service not initialized'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/ses/status', methods=['GET'])
def ses_status():
    """Check SES service status."""
    try:
        service = current_app.config.get('SES_SERVICE')
        if service:
            return jsonify(service.get_status()), 200
        return jsonify({'error': 'SES service not initialized'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/ses/emails', methods=['GET'])
def get_sent_emails():
    """Retrieve the log of sent emails (mock mode only)."""
    try:
        service = current_app.config.get('SES_SERVICE')
        if service:
            return jsonify(service.get_sent_emails()), 200
        return jsonify({'error': 'SES service not initialized'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/comprehend/status', methods=['GET'])
def comprehend_status():
    """Check Comprehend service status."""
    try:
        service = current_app.config.get('COMPREHEND_SERVICE')
        if service:
            return jsonify(service.get_status()), 200
        return jsonify({'error': 'Comprehend service not initialized'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/cloudfront/status', methods=['GET'])
def cloudfront_status():
    """Check CloudFront service status."""
    try:
        service = current_app.config.get('CLOUDFRONT_SERVICE')
        if service:
            return jsonify(service.get_status()), 200
        return jsonify({'error': 'CloudFront service not initialized'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/lambda/status', methods=['GET'])
def lambda_status():
    """Check Lambda service status."""
    try:
        service = current_app.config.get('LAMBDA_SERVICE')
        if service:
            return jsonify(service.get_status()), 200
        return jsonify({'error': 'Lambda service not initialized'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@aws_bp.route('/api/aws/lambda/invocations', methods=['GET'])
def get_lambda_invocations():
    """Retrieve the log of Lambda invocations (mock mode only)."""
    try:
        service = current_app.config.get('LAMBDA_SERVICE')
        if service:
            return jsonify(service.get_invocation_log()), 200
        return jsonify({'error': 'Lambda service not initialized'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500
