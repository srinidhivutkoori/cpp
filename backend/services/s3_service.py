"""
Amazon S3 service for storing uploaded paper PDFs.
Provides both real AWS S3 and mock filesystem-based implementations.
"""

import os
import uuid
from datetime import datetime


class S3Service:
    """
    Manages file storage using Amazon S3 in production
    and local filesystem storage in mock mode.

    Attributes:
        use_aws (bool): Whether to connect to real S3.
        bucket_name (str): S3 bucket name for uploads.
        client: Boto3 S3 client (None in mock mode).
        mock_storage (dict): In-memory file metadata for mock mode.
    """

    def __init__(self, use_aws=False, bucket_name='confpaper-uploads', region='eu-west-1'):
        """
        Initialize the S3 service.

        Args:
            use_aws (bool): If True, connect to real AWS S3.
            bucket_name (str): S3 bucket name.
            region (str): AWS region.
        """
        self.use_aws = use_aws
        self.bucket_name = bucket_name
        self.region = region
        self.client = None
        self.mock_storage = {}
        self.mock_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')

        if self.use_aws:
            import boto3
            self.client = boto3.client('s3', region_name=region)
        else:
            # Ensure local upload directory exists for mock mode
            os.makedirs(self.mock_dir, exist_ok=True)

    def upload_file(self, file_data, file_name, content_type='application/pdf'):
        """
        Upload a file to S3 or local storage.

        Args:
            file_data: File-like object or bytes to upload.
            file_name (str): Original file name.
            content_type (str): MIME type of the file.

        Returns:
            dict: Upload result with file key, URL, and metadata.
        """
        # Generate a unique key for the file
        file_key = f"papers/{uuid.uuid4().hex}/{file_name}"
        timestamp = datetime.utcnow().isoformat()

        if self.use_aws:
            self.client.upload_fileobj(
                file_data,
                self.bucket_name,
                file_key,
                ExtraArgs={'ContentType': content_type}
            )
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{file_key}"
        else:
            # Mock mode: save to local filesystem
            local_path = os.path.join(self.mock_dir, file_key.replace('/', '_'))
            if hasattr(file_data, 'read'):
                content = file_data.read()
                with open(local_path, 'wb') as f:
                    f.write(content)
                file_size = len(content)
            else:
                with open(local_path, 'wb') as f:
                    f.write(file_data)
                file_size = len(file_data)

            url = f"http://localhost:5000/mock-s3/{file_key}"

            self.mock_storage[file_key] = {
                'file_name': file_name,
                'content_type': content_type,
                'size': file_size,
                'local_path': local_path,
                'uploaded_at': timestamp
            }

        return {
            'file_key': file_key,
            'file_name': file_name,
            'url': url,
            'content_type': content_type,
            'uploaded_at': timestamp
        }

    def get_file_url(self, file_key):
        """
        Generate a URL for accessing a stored file.

        Args:
            file_key (str): S3 object key or local file reference.

        Returns:
            str: Presigned URL (AWS) or local URL (mock).
        """
        if self.use_aws:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=3600
            )
            return url
        else:
            return f"http://localhost:5000/mock-s3/{file_key}"

    def delete_file(self, file_key):
        """
        Delete a file from S3 or local storage.

        Args:
            file_key (str): Key of the file to delete.

        Returns:
            bool: True if deletion was successful.
        """
        if self.use_aws:
            self.client.delete_object(Bucket=self.bucket_name, Key=file_key)
        else:
            if file_key in self.mock_storage:
                local_path = self.mock_storage[file_key].get('local_path')
                if local_path and os.path.exists(local_path):
                    os.remove(local_path)
                del self.mock_storage[file_key]

        return True

    def list_files(self, prefix='papers/'):
        """
        List all files with a given prefix in the bucket.

        Args:
            prefix (str): Key prefix to filter by.

        Returns:
            list: List of file metadata dictionaries.
        """
        if self.use_aws:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )
            return [
                {'key': obj['Key'], 'size': obj['Size'],
                 'last_modified': obj['LastModified'].isoformat()}
                for obj in response.get('Contents', [])
            ]
        else:
            return [
                {'key': key, **meta}
                for key, meta in self.mock_storage.items()
                if key.startswith(prefix)
            ]

    def get_status(self):
        """
        Check S3 service status.

        Returns:
            dict: Service status information.
        """
        if self.use_aws:
            try:
                self.client.head_bucket(Bucket=self.bucket_name)
                return {'service': 'S3', 'status': 'connected', 'mode': 'aws',
                        'bucket': self.bucket_name}
            except Exception as e:
                return {'service': 'S3', 'status': 'error', 'error': str(e)}
        else:
            return {
                'service': 'S3',
                'status': 'running',
                'mode': 'mock',
                'files_stored': len(self.mock_storage),
                'storage_dir': self.mock_dir
            }
