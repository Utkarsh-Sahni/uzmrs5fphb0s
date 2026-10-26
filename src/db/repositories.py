from typing import List, Tuple, Optional
from datetime import datetime
from .database import Database

class ElexonRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_actual_generation_for_period(self, date: str, period: int) -> List[Tuple[str, float]]:
        return self.db.get_actual_generation(date, period)

    def get_forecast_for_period_as_of(self, date: str, period: int, decision_time: str) -> Optional[Tuple[float, str]]:
        return self.db.get_forecast_as_of(date, period, decision_time)

    def get_all_periods_for_date(self, date: str) -> List[int]:
        # In reality, this would be 1-48. 
        # For this implementation, we check what's actually in the DB.
        import sqlite3
        with sqlite3.connect(self.db.db_path) as conn:
            cursor = conn.execute(
                "SELECT DISTINCT settlement_period FROM fuel_hh WHERE settlement_date = ?",
                (date,)
            )
            return [row[0] for row in cursor.fetchall()]
