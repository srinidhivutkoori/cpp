"""
Amazon CloudFront service for CDN distribution of frontend assets and paper downloads.
Provides both real AWS CloudFront and mock URL generation.
"""

from datetime import datetime


class CloudFrontService:
    """
    Manages CDN distribution using Amazon CloudFront in production
    and generates mock CDN URLs in development mode.

    Attributes:
        use_aws (bool): Whether to connect to real CloudFront.
        domain_name (str): CloudFront distribution domain.
        distribution_id (str): CloudFront distribution ID.
        client: Boto3 CloudFront client (None in mock mode).
    """

    def __init__(self, use_aws=False, domain_name='d123456789.cloudfront.net',
                 distribution_id='', region='eu-west-1'):
        """
        Initialize the CloudFront service.

        Args:
            use_aws (bool): If True, connect to real AWS CloudFront.
            domain_name (str): CloudFront distribution domain name.
            distribution_id (str): Distribution ID for cache operations.
            region (str): AWS region.
        """
        self.use_aws = use_aws
        self.domain_name = domain_name
        self.distribution_id = distribution_id
        self.region = region
        self.client = None
        self.mock_invalidations = []

        if self.use_aws:
            import boto3
            self.client = boto3.client('cloudfront', region_name=region)

    def get_cdn_url(self, file_key):
        """
        Generate a CloudFront CDN URL for a given file key.

        Args:
            file_key (str): S3 object key or asset path.

        Returns:
            str: Full CDN URL for the resource.
        """
        if self.use_aws:
            return f"https://{self.domain_name}/{file_key}"
        else:
            return f"https://mock-cdn.confpaper.local/{file_key}"

    def get_paper_download_url(self, paper_file_key):
        """
        Generate a CDN-backed download URL for a paper PDF.

        Args:
            paper_file_key (str): S3 key of the paper PDF.

        Returns:
            dict: Download URL with metadata.
        """
        cdn_url = self.get_cdn_url(paper_file_key)
        return {
            'download_url': cdn_url,
            'cdn_domain': self.domain_name if self.use_aws else 'mock-cdn.confpaper.local',
            'file_key': paper_file_key,
            'generated_at': datetime.utcnow().isoformat()
        }

    def invalidate_cache(self, paths):
        """
        Create a cache invalidation for the given paths.

        Args:
            paths (list): List of URL paths to invalidate.

        Returns:
            dict: Invalidation result with ID and status.
        """
        if self.use_aws:
            import time
            response = self.client.create_invalidation(
                DistributionId=self.distribution_id,
                InvalidationBatch={
                    'Paths': {'Quantity': len(paths), 'Items': paths},
                    'CallerReference': str(int(time.time()))
                }
            )
            return {
                'invalidation_id': response['Invalidation']['Id'],
                'status': response['Invalidation']['Status'],
                'paths': paths
            }
        else:
            invalidation = {
                'invalidation_id': f"mock-inv-{len(self.mock_invalidations) + 1:04d}",
                'status': 'Completed',
                'paths': paths,
                'created_at': datetime.utcnow().isoformat()
            }
            self.mock_invalidations.append(invalidation)
            return invalidation

    def get_distribution_info(self):
        """
        Get information about the CloudFront distribution.

        Returns:
            dict: Distribution configuration and status.
        """
        if self.use_aws:
            try:
                response = self.client.get_distribution(Id=self.distribution_id)
                dist = response['Distribution']
                return {
                    'id': dist['Id'],
                    'domain': dist['DomainName'],
                    'status': dist['Status'],
                    'enabled': dist['DistributionConfig']['Enabled']
                }
            except Exception as e:
                return {'error': str(e)}
        else:
            return {
                'id': 'MOCK_DISTRIBUTION_001',
                'domain': 'mock-cdn.confpaper.local',
                'status': 'Deployed',
                'enabled': True,
                'origins': ['confpaper-uploads.s3.amazonaws.com'],
                'price_class': 'PriceClass_100'
            }

    def get_status(self):
        """
        Check CloudFront service status.

        Returns:
            dict: Service status information.
        """
        if self.use_aws:
            try:
                self.client.list_distributions(MaxItems='1')
                return {'service': 'CloudFront', 'status': 'connected', 'mode': 'aws'}
            except Exception as e:
                return {'service': 'CloudFront', 'status': 'error', 'error': str(e)}
        else:
            return {
                'service': 'CloudFront',
                'status': 'running',
                'mode': 'mock',
                'domain': 'mock-cdn.confpaper.local',
                'invalidations': len(self.mock_invalidations)
            }
