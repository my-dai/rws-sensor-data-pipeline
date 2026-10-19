from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Mapping


CHANNELS: dict[str, tuple[str, float | None, float | None]] = {
    "temperature_c": ("C", -80.0, 80.0),
    "pressure_hpa": ("hPa", 250.0, 1_200.0),
    "humidity_pct": ("%", 0.0, 100.0),
    "wind_speed_mps": ("m/s", 0.0, 100.0),
    "wind_direction_deg": ("deg", 0.0, 360.0),
    "rainfall_mm": ("mm", 0.0, None),
    "soil_temperature_c": ("C", -60.0, 80.0),
    "soil_moisture_pct": ("%", 0.0, 100.0),
    "uv_index": ("index", 0.0, 30.0),
    "radon_bq_m3": ("Bq/m3", 0.0, None),
    "geiger_cpm": ("CPM", 0.0, None),
}


@dataclass(frozen=True)
class SensorSample:
    channel: str
    value: float
    unit: str
    source: str


@dataclass(frozen=True)
class Reading:
    station_id: str
    collected_at: str
    values: Mapping[str, float]
    sources: Mapping[str, str]
    errors: Mapping[str, str] = field(default_factory=dict)

    @classmethod
    def now(
        cls,
        station_id: str,
        values: Mapping[str, float],
        sources: Mapping[str, str],
        errors: Mapping[str, str],
    ) -> "Reading":
        timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        return cls(station_id, timestamp, dict(values), dict(sources), dict(errors))


def normalize(sample: SensorSample) -> tuple[str, float]:
    if sample.channel not in CHANNELS:
        raise ValueError(f"unsupported channel: {sample.channel}")

    expected_unit, minimum, maximum = CHANNELS[sample.channel]
    value = float(sample.value)

    if sample.channel.endswith("_c") and sample.unit == "F":
        value = (value - 32.0) * 5.0 / 9.0
    elif sample.channel == "wind_speed_mps" and sample.unit == "mph":
        value *= 0.44704
    elif sample.channel == "rainfall_mm" and sample.unit == "in":
        value *= 25.4
    elif sample.unit != expected_unit:
        raise ValueError(
            f"{sample.channel} expects {expected_unit}, received {sample.unit}"
        )

    if minimum is not None and value < minimum:
        raise ValueError(f"{sample.channel} below valid range")
    if maximum is not None and value > maximum:
        raise ValueError(f"{sample.channel} above valid range")

    return sample.channel, round(value, 4)

