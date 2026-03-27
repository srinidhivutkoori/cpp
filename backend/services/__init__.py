"""
AWS services package for the Academic Conference Paper Submission System.
Provides both real AWS and mock implementations for all six cloud services.
"""

from .dynamodb_service import DynamoDBService
from .s3_service import S3Service
from .ses_service import SESService
from .comprehend_service import ComprehendService
from .cloudfront_service import CloudFrontService
from .lambda_service import LambdaService

__all__ = [
    'DynamoDBService', 'S3Service', 'SESService',
    'ComprehendService', 'CloudFrontService', 'LambdaService'
]
