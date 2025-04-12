import hashlib
import json
from decimal import Decimal
import boto3
import uuid
import os
import time

# Initialize DynamoDB and SQS clients
sqs = boto3.client('sqs')
dynamodb = boto3.resource('dynamodb')

SQS_QUEUE_URL = os.environ['SQS_QUEUE_URL']
TABLE_NAME = "BuildingClashResults"

class BuildingClashHandler:
    def __init__(self):
        """self.redis_url = os.getenv("REDIS_URL")
        if not self.redis_url:
            raise ValueError("REDIS_URL environment variable missing")
        self.service = BuildingClashDetectService(redis_url=self.redis_url)"""

    def handle(self,event, context):
        # Validate and parse the input data
        data = self.parse_input_data(event)
        if not data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Invalid JSON input'})
            }

        task_id = self.generate_task_id(data)

        # Attempt to retrieve the result from DynamoDB
        result = self.fetch_result_from_dynamodb(task_id)
        if result:
            return self.generate_response(200, result)

        # Send the task to SQS for processing
        self.send_task_to_sqs(task_id, data)

        # Poll for the result for up to 10 seconds
        result = self.poll_for_result(task_id)
        if result:
            return self.generate_response(200, result)

        return {
            "statusCode": 202,
            "body": json.dumps({"message": "Processing, please try again later", "task_id": task_id})
        }

    def parse_input_data(self, event):
        """Parse and validate the JSON input from the event."""
        try:
            return json.loads(event['body'])
        except json.JSONDecodeError:
            return None

    def generate_task_id(self, data):
        """Generate a task_id by hashing the input data."""
        input_string = json.dumps(data, sort_keys=True)  # Ensure consistent JSON order
        return hashlib.sha256(input_string.encode('utf-8')).hexdigest()

    def fetch_result_from_dynamodb(self,task_id):
        """Fetch the result from DynamoDB if it exists."""
        table = dynamodb.Table(TABLE_NAME)
        response = table.get_item(Key={"task_id": task_id})
        return response.get('Item')

    def send_task_to_sqs(self,task_id, data):
        """Send the task to SQS for processing."""
        sqs.send_message(
            QueueUrl=SQS_QUEUE_URL,
            MessageBody=json.dumps({
                'task_id': task_id,
                'input': data
            })
        )

    def poll_for_result(self,task_id):
        """Poll DynamoDB for the result for up to 10 seconds."""
        timeout = time.time() + 10
        while time.time() < timeout:
            result = self.fetch_result_from_dynamodb(task_id)
            if result:
                return result
            time.sleep(1)
        return None

    def generate_response(self,status_code, result):
        """Generate a consistent response format."""
        return {
            "statusCode": status_code,
            "body": json.dumps(self.convert_decimal_to_float(result.get("result", result)))
        }

    def convert_decimal_to_float(self,obj):
        """Recursively converts Decimal values to float."""
        if isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, dict):
            return {key: self.convert_decimal_to_float(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_decimal_to_float(item) for item in obj]
        else:
            return obj
# Initialize outside handler for cold-start optimization
handler_instance = BuildingClashHandler()

def handler(event, context):
    return handler_instance.handle(event, context)

