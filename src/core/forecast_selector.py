from src.db.database import Database
from typing import Optional, Tuple

class ForecastSelector:
    def __init__(self, db: Database):
        self.db = db

    def select_forecast(self, target_date: str, target_period: int, decision_time: str) -> Optional[float]:
        """
        Finds the most recent forecast published before or at the decision_time
        for the given target interval.
        """
        result = self.db.get_forecast_as_of(target_date, target_period, decision_time)
        if result:
            # result is (forecast_value_mw, forecast_publish_date_time)
            return result[0]
        return None

    def get_forecast_metadata(self, target_date: str, target_period: int, decision_time: str) -> Optional[Tuple[float, str]]:
        """
        Returns both value and publish time for verification.
        """
        return self.db.get_forecast_as_of(target_date, target_period, decision_time)
