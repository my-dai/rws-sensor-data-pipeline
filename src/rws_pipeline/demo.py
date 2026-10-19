from __future__ import annotations

import argparse
import random
from dataclasses import dataclass

from .models import SensorSample
from .pipeline import CollectionPipeline
from .storage import SQLiteReadingStore


@dataclass
class SyntheticEnvironmentSensor:
    name: str = "environment"

    def read(self) -> list[SensorSample]:
        return [
            SensorSample("temperature_c", random.uniform(17, 27), "C", self.name),
            SensorSample("pressure_hpa", random.uniform(985, 1_025), "hPa", self.name),
            SensorSample("humidity_pct", random.uniform(30, 75), "%", self.name),
        ]


@dataclass
class SyntheticRadiationSensor:
    name: str = "radiation"

    def read(self) -> list[SensorSample]:
        return [
            SensorSample("radon_bq_m3", random.uniform(5, 80), "Bq/m3", self.name),
            SensorSample("geiger_cpm", random.uniform(8, 35), "CPM", self.name),
        ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cycles", type=int, default=5)
    parser.add_argument("--database", default="demo.sqlite")
    parser.add_argument("--csv", default="demo.csv")
    args = parser.parse_args()

    pipeline = CollectionPipeline(
        "synthetic-station", [SyntheticEnvironmentSensor(), SyntheticRadiationSensor()]
    )
    store = SQLiteReadingStore(args.database)
    for _ in range(args.cycles):
        store.append(pipeline.collect())
    store.export_csv(args.csv)
    print(f"stored {len(store.all())} readings and exported {args.csv}")


if __name__ == "__main__":
    main()

