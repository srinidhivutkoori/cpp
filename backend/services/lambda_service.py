"""
AWS Lambda service for asynchronous paper processing and review assignment.
Provides both real AWS Lambda invocation and mock processing.
"""

import json
import random
from datetime import datetime


class LambdaService:
    """
    Manages serverless function invocations using AWS Lambda in production
    and simulates async processing in mock mode.

    Attributes:
        use_aws (bool): Whether to connect to real Lambda.
        function_prefix (str): Prefix for Lambda function names.
        client: Boto3 Lambda client (None in mock mode).
        mock_invocations (list): Log of mock invocations.
    """

    def __init__(self, use_aws=False, function_prefix='confpaper_', region='eu-west-1'):
        """
        Initialize the Lambda service.

        Args:
            use_aws (bool): If True, connect to real AWS Lambda.
            function_prefix (str): Prefix for Lambda function names.
            region (str): AWS region.
        """
        self.use_aws = use_aws
        self.function_prefix = function_prefix
        self.region = region
        self.client = None
        self.mock_invocations = []

        if self.use_aws:
            import boto3
            self.client = boto3.client('lambda', region_name=region)

    def invoke_function(self, function_name, payload):
        """
        Invoke a Lambda function with the given payload.

        Args:
            function_name (str): Name of the Lambda function.
            payload (dict): Input data for the function.

        Returns:
            dict: Invocation result with response data.
        """
        full_name = f"{self.function_prefix}{function_name}"
        timestamp = datetime.utcnow().isoformat()

        if self.use_aws:
            response = self.client.invoke(
                FunctionName=full_name,
                InvocationType='Event',  # Async invocation
                Payload=json.dumps(payload)
            )
            return {
                'function': full_name,
                'status_code': response['StatusCode'],
                'invoked_at': timestamp
            }
        else:
            # Mock mode: simulate the function execution
            invocation = {
                'function': full_name,
                'payload': payload,
                'status_code': 202,
                'invoked_at': timestamp,
                'request_id': f"mock-req-{len(self.mock_invocations) + 1:04d}"
            }
            self.mock_invocations.append(invocation)
            return invocation

    def process_paper_submission(self, paper_id, abstract_text):
        """
        Trigger async processing of a newly submitted paper.
        In production this invokes a Lambda for NLP analysis and metadata extraction.

        Args:
            paper_id (int): ID of the submitted paper.
            abstract_text (str): Paper abstract for NLP processing.

        Returns:
            dict: Processing task result.
        """
        payload = {
            'action': 'process_paper',
            'paper_id': paper_id,
            'abstract_text': abstract_text,
            'tasks': ['nlp_analysis', 'keyword_extraction', 'similarity_check']
        }
        result = self.invoke_function('paper_processor', payload)
        result['processing_tasks'] = payload['tasks']
        return result

    def assign_reviewers(self, paper_id, paper_keywords, available_reviewers):
        """
        Trigger async reviewer assignment using expertise matching.

        Args:
            paper_id (int): ID of the paper to assign reviewers for.
            paper_keywords (list): Paper keywords for matching.
            available_reviewers (list): List of available reviewer data.

        Returns:
            dict: Assignment task result with suggested reviewers.
        """
        payload = {
            'action': 'assign_reviewers',
            'paper_id': paper_id,
            'paper_keywords': paper_keywords,
            'reviewer_count': len(available_reviewers)
        }
        result = self.invoke_function('reviewer_assigner', payload)

        if not self.use_aws:
            # Mock mode: simulate reviewer assignment suggestions
            num_to_assign = min(3, len(available_reviewers))
            suggested = random.sample(available_reviewers, num_to_assign) if available_reviewers else []
            result['suggested_reviewers'] = suggested
            result['matching_scores'] = [
                round(random.uniform(0.6, 0.95), 3) for _ in suggested
            ]

        return result

    def generate_decision(self, paper_id, review_scores):
        """
        Trigger async decision generation based on review scores.

        Args:
            paper_id (int): ID of the paper.
            review_scores (list): List of review score dictionaries.

        Returns:
            dict: Decision task result with recommendation.
        """
        payload = {
            'action': 'generate_decision',
            'paper_id': paper_id,
            'review_scores': review_scores
        }
        result = self.invoke_function('decision_generator', payload)

        if not self.use_aws:
            # Mock mode: generate a decision based on average scores
            if review_scores:
                avg = sum(r.get('overall_score', 5) for r in review_scores) / len(review_scores)
                if avg >= 7:
                    decision = 'accepted'
                elif avg >= 5:
                    decision = 'borderline'
                else:
                    decision = 'rejected'
            else:
                decision = 'pending'

            result['recommended_decision'] = decision
            result['average_score'] = round(avg, 2) if review_scores else None

        return result

    def get_invocation_log(self):
        """
        Get the log of all Lambda invocations (mock mode).

        Returns:
            list: List of invocation records.
        """
        return self.mock_invocations

    def get_status(self):
        """
        Check Lambda service status.

        Returns:
            dict: Service status information.
        """
        if self.use_aws:
            try:
                self.client.list_functions(MaxItems=1)
                return {'service': 'Lambda', 'status': 'connected', 'mode': 'aws'}
            except Exception as e:
                return {'service': 'Lambda', 'status': 'error', 'error': str(e)}
        else:
            return {
                'service': 'Lambda',
                'status': 'running',
                'mode': 'mock',
                'invocations': len(self.mock_invocations),
                'functions': [
                    f'{self.function_prefix}paper_processor',
                    f'{self.function_prefix}reviewer_assigner',
                    f'{self.function_prefix}decision_generator'
                ]
            }
