from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from .models import Reading, SensorSample, normalize


class Sensor(Protocol):
    name: str

    def read(self) -> Iterable[SensorSample]: ...


class CollectionPipeline:
    """Collect one station snapshot without letting one sensor erase good data."""

    def __init__(self, station_id: str, sensors: Iterable[Sensor]):
        self.station_id = station_id
        self.sensors = list(sensors)

    def collect(self) -> Reading:
        values: dict[str, float] = {}
        sources: dict[str, str] = {}
        errors: dict[str, str] = {}

        for sensor in self.sensors:
            try:
                for sample in sensor.read():
                    channel, value = normalize(sample)
                    if channel in values:
                        raise ValueError(f"duplicate channel: {channel}")
                    values[channel] = value
                    sources[channel] = sample.source
            except Exception as exc:  # device boundaries must isolate failures
                errors[sensor.name] = f"{type(exc).__name__}: {exc}"

        return Reading.now(self.station_id, values, sources, errors)

