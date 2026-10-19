from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
import struct

from .models import SensorSample


@dataclass(frozen=True)
class PulseChannel:
    """Convert GPIO edge counts into a physical measurement."""

    channel: str
    unit: str
    source: str
    scale_per_pulse: float

    def sample(self, pulses: int, elapsed_seconds: float) -> SensorSample:
        if pulses < 0:
            raise ValueError("pulse count cannot be negative")
        if elapsed_seconds <= 0:
            raise ValueError("elapsed time must be positive")
        rate_per_minute = pulses * 60.0 / elapsed_seconds
        return SensorSample(
            self.channel,
            rate_per_minute * self.scale_per_pulse,
            self.unit,
            self.source,
        )


class GPIOPulseSensor:
    """Hardware-neutral edge counter for Geiger, rain, or anemometer inputs.

    A Raspberry Pi deployment supplies a callback that atomically returns and
    resets the interrupt count. Tests and demos can use the same interface
    without importing a board-specific GPIO package.
    """

    def __init__(
        self,
        name: str,
        counter: Callable[[], tuple[int, float]],
        channel: PulseChannel,
    ):
        self.name = name
        self._counter = counter
        self._channel = channel

    def read(self) -> Iterable[SensorSample]:
        pulses, elapsed_seconds = self._counter()
        return [self._channel.sample(pulses, elapsed_seconds)]


class RadonBleSensor:
    """Decode a compact BLE radon notification into the shared station schema."""

    name = "radon_ble"

    def __init__(self, payload_reader: Callable[[], bytes], source: str = "RadonEye BLE"):
        self._payload_reader = payload_reader
        self._source = source

    @staticmethod
    def decode(payload: bytes) -> float:
        if len(payload) < 4:
            raise ValueError("radon BLE payload is too short")
        # Portfolio protocol: little-endian float in pCi/L. A deployment
        # adapter can isolate its device-specific frame before calling here.
        pci_l = struct.unpack("<f", payload[:4])[0]
        if not 0.0 <= pci_l <= 10_000.0:
            raise ValueError("radon BLE payload is outside the supported range")
        return pci_l * 37.0

    def read(self) -> Iterable[SensorSample]:
        value = self.decode(self._payload_reader())
        return [SensorSample("radon_bq_m3", value, "Bq/m3", self._source)]


class MappedSensor:
    """Map a multi-channel device/API response into station fields."""

    def __init__(
        self,
        name: str,
        reader: Callable[[], Mapping[str, float]],
        channel_map: Mapping[str, tuple[str, str]],
    ):
        self.name = name
        self._reader = reader
        self._channel_map = dict(channel_map)

    def read(self) -> Iterable[SensorSample]:
        raw = self._reader()
        samples = [
            SensorSample(channel, raw[raw_name], unit, self.name)
            for raw_name, (channel, unit) in self._channel_map.items()
            if raw_name in raw
        ]
        if not samples:
            raise ValueError("device returned no configured channels")
        return samples


ENVIRONMENT_CHANNELS = {
    "temperature": ("temperature_c", "C"),
    "pressure": ("pressure_hpa", "hPa"),
    "humidity": ("humidity_pct", "%"),
    "gas": ("gas_resistance_ohm", "ohm"),
}

WEATHER_CHANNELS = {
    "wind_speed": ("wind_speed_mps", "m/s"),
    "wind_direction": ("wind_direction_deg", "deg"),
    "rainfall": ("rainfall_mm", "mm"),
    "uv": ("uv_index", "index"),
}

SOIL_CHANNELS = {
    "temperature": ("soil_temperature_c", "C"),
    "moisture": ("soil_moisture_pct", "%"),
}
