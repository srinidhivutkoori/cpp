"""
Amazon DynamoDB service for storing conferences, papers, reviews, and authors.
Provides both real AWS DynamoDB and mock in-memory implementations.
"""

import json
import uuid
from datetime import datetime


class DynamoDBService:
    """
    Manages data persistence using Amazon DynamoDB in production
    and an in-memory dictionary store in mock mode.

    Attributes:
        use_aws (bool): Whether to connect to real DynamoDB.
        region (str): AWS region for the DynamoDB endpoint.
        client: Boto3 DynamoDB client (None in mock mode).
        mock_tables (dict): In-memory table storage for mock mode.
    """

    def __init__(self, use_aws=False, region='eu-west-1'):
        """
        Initialize the DynamoDB service.

        Args:
            use_aws (bool): If True, connect to real AWS DynamoDB.
            region (str): AWS region for DynamoDB.
        """
        self.use_aws = use_aws
        self.region = region
        self.client = None
        self.mock_tables = {
            'conferences': {},
            'papers': {},
            'reviews': {},
            'authors': {}
        }

        if self.use_aws:
            import boto3
            self.client = boto3.resource('dynamodb', region_name=region)

    def put_item(self, table_name, item):
        """
        Insert or update an item in a DynamoDB table.

        Args:
            table_name (str): Target table name.
            item (dict): Item data to store.

        Returns:
            dict: The stored item with generated ID if not present.
        """
        if not item.get('id'):
            item['id'] = str(uuid.uuid4())
        item['updated_at'] = datetime.utcnow().isoformat()

        if self.use_aws:
            table = self.client.Table(table_name)
            table.put_item(Item=item)
        else:
            # Mock mode: store in memory
            self.mock_tables.setdefault(table_name, {})
            self.mock_tables[table_name][item['id']] = item

        return item

    def get_item(self, table_name, item_id):
        """
        Retrieve a single item by its ID from a DynamoDB table.

        Args:
            table_name (str): Source table name.
            item_id (str): Unique identifier of the item.

        Returns:
            dict or None: The item data, or None if not found.
        """
        if self.use_aws:
            table = self.client.Table(table_name)
            response = table.get_item(Key={'id': item_id})
            return response.get('Item')
        else:
            return self.mock_tables.get(table_name, {}).get(item_id)

    def get_all_items(self, table_name):
        """
        Retrieve all items from a DynamoDB table.

        Args:
            table_name (str): Source table name.

        Returns:
            list: List of all items in the table.
        """
        if self.use_aws:
            table = self.client.Table(table_name)
            response = table.scan()
            return response.get('Items', [])
        else:
            return list(self.mock_tables.get(table_name, {}).values())

    def delete_item(self, table_name, item_id):
        """
        Delete an item from a DynamoDB table by its ID.

        Args:
            table_name (str): Target table name.
            item_id (str): Unique identifier of the item to delete.

        Returns:
            bool: True if deletion was successful.
        """
        if self.use_aws:
            table = self.client.Table(table_name)
            table.delete_item(Key={'id': item_id})
        else:
            if table_name in self.mock_tables and item_id in self.mock_tables[table_name]:
                del self.mock_tables[table_name][item_id]

        return True

    def query_by_attribute(self, table_name, attribute, value):
        """
        Query items in a table by a specific attribute value.

        Args:
            table_name (str): Source table name.
            attribute (str): Attribute name to filter by.
            value: Expected value for the attribute.

        Returns:
            list: Matching items.
        """
        if self.use_aws:
            table = self.client.Table(table_name)
            response = table.scan(
                FilterExpression=f'{attribute} = :val',
                ExpressionAttributeValues={':val': value}
            )
            return response.get('Items', [])
        else:
            results = []
            for item in self.mock_tables.get(table_name, {}).values():
                if item.get(attribute) == value:
                    results.append(item)
            return results

    def get_status(self):
        """
        Check the service status and connectivity.

        Returns:
            dict: Service status information.
        """
        if self.use_aws:
            try:
                self.client.meta.client.list_tables()
                return {'service': 'DynamoDB', 'status': 'connected', 'mode': 'aws'}
            except Exception as e:
                return {'service': 'DynamoDB', 'status': 'error', 'error': str(e)}
        else:
            table_counts = {k: len(v) for k, v in self.mock_tables.items()}
            return {
                'service': 'DynamoDB',
                'status': 'running',
                'mode': 'mock',
                'tables': table_counts
            }
