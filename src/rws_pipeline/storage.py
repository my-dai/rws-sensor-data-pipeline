from __future__ import annotations

import csv
import json
import sqlite3
from contextlib import closing
from pathlib import Path

from .models import CHANNELS, Reading


class SQLiteReadingStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.execute("PRAGMA journal_mode=WAL")
        return connection

    def _initialize(self) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY,
                    station_id TEXT NOT NULL,
                    collected_at TEXT NOT NULL,
                    values_json TEXT NOT NULL,
                    sources_json TEXT NOT NULL,
                    errors_json TEXT NOT NULL,
                    UNIQUE(station_id, collected_at)
                )
                """
            )

    def append(self, reading: Reading) -> None:
        with closing(self._connect()) as connection, connection:
            connection.execute(
                """
                INSERT INTO readings
                    (station_id, collected_at, values_json, sources_json, errors_json)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    reading.station_id,
                    reading.collected_at,
                    json.dumps(reading.values, sort_keys=True),
                    json.dumps(reading.sources, sort_keys=True),
                    json.dumps(reading.errors, sort_keys=True),
                ),
            )

    def all(self) -> list[Reading]:
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT station_id, collected_at, values_json, sources_json, errors_json
                FROM readings ORDER BY collected_at, id
                """
            ).fetchall()
        return [
            Reading(station, timestamp, json.loads(values), json.loads(sources), json.loads(errors))
            for station, timestamp, values, sources, errors in rows
        ]

    def export_csv(self, path: str | Path) -> None:
        fieldnames = ["station_id", "collected_at", *CHANNELS, "errors"]
        with Path(path).open("w", encoding="utf-8", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            for reading in self.all():
                row: dict[str, object] = {
                    "station_id": reading.station_id,
                    "collected_at": reading.collected_at,
                    "errors": json.dumps(reading.errors, sort_keys=True),
                }
                row.update(reading.values)
                writer.writerow(row)

