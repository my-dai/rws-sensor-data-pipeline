# Radiation Weather Station Data Pipeline

[![Test](https://github.com/my-dai/rws-sensor-data-pipeline/actions/workflows/test.yml/badge.svg)](https://github.com/my-dai/rws-sensor-data-pipeline/actions/workflows/test.yml)

A hardware-independent version of the data pipeline I developed for a Raspberry
Pi radiation and weather station at the University of Michigan Radiological
Health Engineering Lab.

My work centered on turning readings from different instruments into a
consistent timestamped record, validating and normalizing those readings,
storing them in SQLite, and exporting analysis-ready CSV data. The adapters in
this repository generate sample readings so the collection loop can run without
lab hardware.

## Pipeline coverage

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

The test suite currently contains seven tests covering conversion, validation,
partial failures, persistence, and export behavior.

## Project context

The lab system also used Raspberry Pi GPIO interrupts, BLE, HTTP APIs, local and
cloud storage, and environmental and radiation instruments. Device-specific
drivers are isolated behind small adapters here so acquisition, validation,
persistence, and export can be tested without the station. Lab credentials,
research data, and deployment configuration are not included.

