from pathlib import Path
import tempfile
import unittest

from rws_pipeline.models import SensorSample, normalize
from rws_pipeline.pipeline import CollectionPipeline
from rws_pipeline.storage import SQLiteReadingStore


class GoodSensor:
    name = "good"

    def read(self):
        return [
            SensorSample("temperature_c", 68.0, "F", self.name),
            SensorSample("wind_speed_mps", 10.0, "mph", self.name),
        ]


class FailedSensor:
    name = "failed"

    def read(self):
        raise TimeoutError("BLE response timeout")


class PipelineTests(unittest.TestCase):
    def test_units_are_normalized(self):
        self.assertEqual(
            normalize(SensorSample("temperature_c", 68.0, "F", "sensor"))[1], 20.0
        )
        self.assertEqual(
            normalize(SensorSample("rainfall_mm", 1.0, "in", "sensor"))[1], 25.4
        )

    def test_invalid_range_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "above valid range"):
            normalize(SensorSample("humidity_pct", 120.0, "%", "sensor"))

    def test_partial_failure_preserves_valid_channels(self):
        reading = CollectionPipeline("station-1", [GoodSensor(), FailedSensor()]).collect()
        self.assertEqual(reading.values["temperature_c"], 20.0)
        self.assertEqual(reading.values["wind_speed_mps"], 4.4704)
        self.assertIn("failed", reading.errors)

    def test_sqlite_round_trip_and_csv_export(self):
        with tempfile.TemporaryDirectory() as directory:
            temp_path = Path(directory)
            reading = CollectionPipeline("station-1", [GoodSensor()]).collect()
            store = SQLiteReadingStore(temp_path / "readings.sqlite")
            store.append(reading)
            restored = store.all()
            self.assertEqual(restored[0].values, reading.values)

            csv_path = temp_path / "readings.csv"
            store.export_csv(csv_path)
            content = csv_path.read_text(encoding="utf-8")
            self.assertIn("temperature_c", content)
            self.assertIn("station-1", content)


if __name__ == "__main__":
    unittest.main()

