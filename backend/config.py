"""
Configuration module for Academic Conference Paper Submission System.
Provides environment-specific settings for development, testing, and production.
Student: Srinidhi Vutkoori (X25173243)
"""

import os


class Config:
    """Base configuration with shared settings across all environments."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-srinidhi-x25173243')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS Configuration - defaults to mock mode for local development
    USE_AWS = os.environ.get('USE_AWS', 'False').lower() == 'true'

    # AWS Credentials (only used when USE_AWS=True)
    AWS_REGION = os.environ.get('AWS_REGION', 'eu-west-1')
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')

    # DynamoDB Configuration
    DYNAMODB_TABLE_PREFIX = os.environ.get('DYNAMODB_TABLE_PREFIX', 'confpaper_')

    # S3 Configuration
    S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME', 'confpaper-uploads')
    S3_MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB max file size

    # SES Configuration
    SES_SENDER_EMAIL = os.environ.get('SES_SENDER_EMAIL', 'noreply@confpaper.example.com')
    SES_REGION = os.environ.get('SES_REGION', 'eu-west-1')

    # Comprehend Configuration
    COMPREHEND_LANGUAGE = 'en'

    # CloudFront Configuration
    CLOUDFRONT_DOMAIN = os.environ.get('CLOUDFRONT_DOMAIN', 'd123456789.cloudfront.net')
    CLOUDFRONT_DISTRIBUTION_ID = os.environ.get('CLOUDFRONT_DISTRIBUTION_ID', '')

    # Lambda Configuration
    LAMBDA_FUNCTION_PREFIX = os.environ.get('LAMBDA_FUNCTION_PREFIX', 'confpaper_')

    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf'}


class DevelopmentConfig(Config):
    """Development configuration with SQLite and debug mode enabled."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DEV_DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'dev.db')
    )
    USE_AWS = False


class TestingConfig(Config):
    """Testing configuration with in-memory SQLite and AWS mocks."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    USE_AWS = False


class ProductionConfig(Config):
    """Production configuration using DynamoDB and real AWS services."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(os.path.dirname(__file__), 'prod.db')
    )
    USE_AWS = os.environ.get('USE_AWS', 'True').lower() == 'true'


# Configuration dictionary for easy selection by environment name
config_by_name = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
