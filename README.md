# Radiation Weather Station Data Pipeline

A compact, hardware-independent version of the data pipeline I developed for a
Raspberry Pi radiation and weather station at the University of Michigan
Radiological Health Engineering Lab.

The project demonstrates the part of the system I owned: turning heterogeneous
sensor readings into a consistent, timestamped record; validating readings;
storing them locally in SQLite; and exporting analysis-ready CSV data. The demo
uses synthetic sensor adapters so it can run without lab hardware or research
data.

## What it shows

- A shared schema for temperature, pressure, humidity, gas, wind speed and
  direction, rainfall, soil temperature and moisture, UV, radon, and Geiger CPM
- Unit normalization and range validation at the acquisition boundary
- Hardware-neutral GPIO pulse acquisition for Geiger, rain-gauge, and
  anemometer inputs
- BLE payload decoding for RadonEye-style radon measurements
- Multi-channel adapters for environmental, weather, and soil instruments
- A fault-tolerant collection cycle that preserves valid channels when one
  sensor fails
- Transactional SQLite storage and deterministic CSV export
- Tests for validation, partial sensor failure, persistence, and output format

## Run

```bash
python -m rws_pipeline.demo --cycles 5 --database demo.sqlite --csv demo.csv
python -m unittest discover -s tests -v
```

Python 3.11+ is recommended. The package and test suite use only the standard
library.

## Project context

The original lab system integrated Raspberry Pi GPIO interrupts, BLE, HTTP APIs,
local and cloud storage, and environmental and radiation instruments. This
repository is an independent portfolio implementation of the software
architecture and data logic I worked on. Device-specific drivers are isolated
behind small adapters so the acquisition, validation, persistence, and export
layers can be tested without the lab hardware. It contains no lab credentials,
private source code, research data, or deployment configuration.

