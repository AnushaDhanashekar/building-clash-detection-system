import json
import os
import boto3
import uuid
import logging
from typing import Dict, Any
dynamodb = boto3.resource('dynamodb')

from pypackages.detect_building_clash.building_clash_detect_service import BuildingClashDetectService

# Structured logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)
formatter = logging.Formatter('{"time": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

TABLE_NAME = "BuildingClashResults"

class PostSqsLambdaHandler:
    def __init__(self):
        """self.redis_url = os.getenv("REDIS_URL")
        if not self.redis_url:
            raise ValueError("REDIS_URL environment variable missing")
        self.service = BuildingClashDetectService(redis_url=self.redis_url)"""

    def handle(self, event: Dict[str, Any], context) -> Dict[str, Any]:
        """
            Expects a GeoJSON FeatureCollection in `event`
            """
        try:
            logger.info("Starting clash detection")
            service = BuildingClashDetectService()
            response = service.execute(event)
            return {
                "statusCode": 200,
                "body": json.dumps(response)
            }
        except Exception as e:
            logger.error(f"Lambda error: {str(e)}")
            return {
                "statusCode": 500,
                "body": json.dumps({"error": str(e)})
            }
# Initialize outside handler for cold-start optimization
handler_instance = PostSqsLambdaHandler()

def handler(event, context):
    return handler_instance.handle(event, context)