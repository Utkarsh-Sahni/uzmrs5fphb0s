import sqlite3
from datetime import datetime
from typing import List, Tuple, Optional

class Database:
    def __init__(self, db_path: str = "gridbrick.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            with open("src/db/schema.sql", "r") as f:
                conn.executescript(f.read())

    def insert_fuel_hh(self, records: List[Tuple]):
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO fuel_hh VALUES (?, ?, ?, ?, ?)",
                records
            )

    def insert_wind_for(self, records: List[Tuple]):
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO wind_for VALUES (?, ?, ?, ?)",
                records
            )

    def get_actual_generation(self, date: str, period: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT fuel_type, value_mw FROM fuel_hh WHERE settlement_date = ? AND settlement_period = ?",
                (date, period)
            )
            return cursor.fetchall()

    def get_forecast_as_of(self, target_date: str, target_period: int, decision_time: str):
        """
        Returns the latest forecast for a target interval that was published
        before or at the decision_time, and is not retrospective.
        """
        with sqlite3.connect(self.db_path) as conn:
            # target_period is assumed to be 1-24 (hourly)
            # We need to check if it's retrospective.
            # Since we don't have the target_timestamp in the table,
            # we can calculate it or join if we had a mapping.
            # However, the table 'wind_for' has target_date and target_period.

            # To handle the retrospective check (startTime < publishTime),
            # we need the actual target timestamp.
            # Assuming target_period 1 = 00:00-01:00, etc.

            cursor = conn.execute(
                """
                SELECT forecast_value_mw, forecast_publish_date_time
                FROM wind_for
                WHERE target_date = ? AND target_period = ? AND forecast_publish_date_time <= ?
                ORDER BY forecast_publish_date_time DESC
                LIMIT 100
                """,
                (target_date, target_period, decision_time)
            )
            rows = cursor.fetchall()

            # Filter retrospective in Python because the timestamp calculation
            # is easier there than in SQLite (which has limited date math).
            for row in rows:
                val, publish_time_str = row
                publish_time = datetime.fromisoformat(publish_time_str.replace("Z", "+00:00"))

                # Calculate target timestamp
                # target_date is 'YYYY-MM-DD'
                # target_period is 1-24
                target_dt = datetime.strptime(target_date, "%Y-%m-%d").replace(tzinfo=publish_time.tzinfo)
                target_dt += timedelta(hours=target_period - 1)

                if target_dt >= publish_time:
                    return (val, publish_time_str)

            return None
