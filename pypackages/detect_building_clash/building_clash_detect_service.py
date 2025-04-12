import json
import logging
import math
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

from shapely.geometry import Polygon, MultiPolygon
from shapely.geometry.polygon import orient
from pydantic import BaseModel, ValidationError
import boto3
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table("BuildingClashResults")

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@dataclass
class ClashResult:
    elevation: float
    height: float
    building_ids: List[str]
    geometry: List[Tuple[float, float]]


class BuildingFeature(BaseModel):
    """Pydantic model for input validation"""
    id: str
    properties: Dict[str, float]
    geometry: Dict[str, Any]


class BuildingClashDetectService:
    def execute(self, event: dict) -> Dict:
        """Entry point for clash detection"""
        try:
            record = event.get("Records", [])[0]
            input_data = json.loads(record["body"])

            logger.info(f"Received input data: {input_data}")
            print(input_data)

            data = input_data.get("input", input_data)
            task_id = input_data.get("task_id", input_data)

            validated_data = self._validate_input(data)
            results = self._process_features(validated_data["features"])
            self.save_result(task_id=task_id, result={
                "type": "FeatureCollection",
                "features": self.format_results(results)
            })
            print(self.format_results(results))

            return {
                "type": "FeatureCollection",
                "features": self.format_results(results)
            }

        except ValidationError as e:
            logger.error(f"Validation error: {e.json()}")
            raise ValueError("Invalid input format") from e
        except Exception as e:
            logger.error(f"Execution failed: {str(e)}", exc_info=True)
            raise

    def save_result(self, task_id: str, result: Dict):
        table.put_item(Item={
            "task_id": task_id,
            "result": result
        })

    def _validate_input(self, data: Dict) -> Dict:
        if not isinstance(data.get("features"), list):
            raise ValueError("Missing 'features' array")
        features = [BuildingFeature(**f) for f in data["features"]]
        return {"features": features}

    def get_polygon(self, feature: BuildingFeature) -> Polygon:
        coords = feature.geometry["coordinates"][0]
        return Polygon(coords)

    def _process_features(self, features: List[BuildingFeature]) -> List[ClashResult]:
        result_features = []
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                clash = self.calculate_overlap_and_metadata(features[i], features[j])
                if clash:
                    result_features.append(clash)
        return result_features

    def calculate_overlap_and_metadata(
        self, f1: BuildingFeature, f2: BuildingFeature
    ) -> Optional[ClashResult]:
        poly1 = self.get_polygon(f1)
        poly2 = self.get_polygon(f2)
        intersection = poly1.intersection(poly2)

        if not intersection.is_empty and intersection.area > 0:
            elev1 = f1.properties["elevation"]
            elev2 = f2.properties["elevation"]
            height1 = f1.properties["height"]
            height2 = f2.properties["height"]

            top1 = elev1 + height1
            top2 = elev2 + height2

            overlap_elevation = max(elev1, elev2)
            overlap_top = min(top1, top2)
            overlap_height = max(0, overlap_top - overlap_elevation)

            if overlap_height <= 0:
                return None

            if intersection.geom_type == "Polygon":
                coords = list(orient(intersection, sign=1.0).exterior.coords)
            elif intersection.geom_type == "MultiPolygon":
                largest = max(intersection.geoms, key=lambda g: g.area)
                coords = list(orient(largest, sign=1.0).exterior.coords)
            else:
                return None

            cleaned_coords = [(round(x, 6), round(y, 6)) for x, y in coords]
            if cleaned_coords[0] != cleaned_coords[-1]:
                cleaned_coords.append(cleaned_coords[0])

            return ClashResult(
                elevation=overlap_elevation,
                height=overlap_height,
                building_ids=sorted([f1.id, f2.id]),
                geometry=cleaned_coords
            )

        return None

    def rotate_ring_to_start(self,ring: List[Tuple[float, float]]) -> List[List[float]]:
        """Rotate the polygon ring so it always starts at the top-left-most point."""
        min_index = min(range(len(ring)), key=lambda i: (ring[i][1], ring[i][0]))  # y (top), then x (left)
        rotated = ring[min_index:] + ring[1:min_index + 1]  # Ensure it's closed by skipping the duplicate point
        return [[int(x) if float(x).is_integer() else x, int(y) if float(y).is_integer() else y] for x, y in rotated]

    def format_results(self, clashes: List[ClashResult]) -> List[Dict]:
        formatted = []
        for clash in clashes:
            rotated_coords = self.rotate_ring_to_start(clash.geometry)
            formatted.append({
                "type": "Feature",
                "properties": {
                    "elevation": int(clash.elevation) if clash.elevation.is_integer() else clash.elevation,
                    "height": int(clash.height) if clash.height.is_integer() else clash.height,
                    "buildings": clash.building_ids,
                },
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [rotated_coords]
                }
            })
        return self.convert_floats_to_decimal(formatted)

    # Convert all float values to Decimal recursively
    def convert_floats_to_decimal(self,d):
        if isinstance(d, dict):
            return {key: self.convert_floats_to_decimal(value) for key, value in d.items()}
        elif isinstance(d, list):
            return [self.convert_floats_to_decimal(item) for item in d]
        elif isinstance(d, float):
            return Decimal(str(d))  # Convert float to Decimal
        else:
            return d

