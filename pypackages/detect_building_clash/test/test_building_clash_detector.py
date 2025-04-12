import unittest
import json
from decimal import Decimal
from unittest.mock import patch, MagicMock

from pypackages.detect_building_clash.building_clash_detect_service import BuildingClashDetectService


class TestBuildingClashDetectServiceWithRealInput(unittest.TestCase):
    def setUp(self):
        self.event = {
            'Records': [{
                'body': json.dumps({
                    "task_id": "test-task-id",
                    "input": {
                        "features": [
                            {
                                "type": "Feature",
                                "id": "building_0",
                                "properties": {"height": 4, "elevation": 0},
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [[[20, 0], [20, 60], [0, 60], [0, 0], [20, 0]]]
                                }
                            },
                            {
                                "type": "Feature",
                                "id": "building_1",
                                "properties": {"height": 4, "elevation": 2},
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [[[60, 60], [0, 60], [0, 40], [60, 40], [60, 60]]]
                                }
                            }
                        ]
                    }
                })
            }]
        }

    @patch.object(BuildingClashDetectService, 'save_result')
    def test_execute_with_real_input(self, mock_save_result):
        service = BuildingClashDetectService()
        result = service.execute(self.event)

        # Verify basic structure
        self.assertEqual(result["type"], "FeatureCollection")
        self.assertIsInstance(result["features"], list)
        self.assertGreater(len(result["features"]), 0)

        # Verify save_result was called
        mock_save_result.assert_called_once_with(
            task_id='test-task-id',
            result=result
        )

        # Verify the actual overlap calculation
        self.assertEqual(len(result["features"]), 1)
        feature = result["features"][0]
        self.assertEqual(feature["properties"]["elevation"], 2)
        self.assertEqual(feature["properties"]["height"], 2)
        self.assertEqual(sorted(feature["properties"]["buildings"]),
                         ["building_0", "building_1"])

    @patch('pypackages.detect_building_clash.building_clash_detect_service.logger')
    def test_error_handling(self, mock_logger):
        service = BuildingClashDetectService()

        # Test with malformed input
        bad_event = {'Records': [{'body': 'invalid json'}]}
        with self.assertRaises(ValueError):
            service.execute(bad_event)
        mock_logger.error.assert_called()

        # Test with missing features
        bad_event = {'Records': [{'body': json.dumps({"task_id": "test", "input": {}})}]}
        with self.assertRaises(ValueError):
            service.execute(bad_event)
        mock_logger.error.assert_called()


if __name__ == '__main__':
    unittest.main()