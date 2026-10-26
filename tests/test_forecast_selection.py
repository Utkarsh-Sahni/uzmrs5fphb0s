import unittest
import os
import sqlite3
from src.db.database import Database
from src.core.forecast_selector import ForecastSelector

class TestForecastSelection(unittest.TestCase):
    def setUp(self):
        self.db_path = "test_gridbrick.db"
        self.db = Database(self.db_path)
        self.selector = ForecastSelector(self.db)
        
        # Setup test data
        target_date = "2026-01-15"
        target_period = 17
        
        # Forecasts: one before, one after cutoff
        self.db.insert_wind_for([
            ("2026-01-14T10:00:00", target_date, target_period, 100.0),
            ("2026-01-14T11:00:00", target_date, target_period, 110.0), # Exactly at cutoff
            ("2026-01-14T11:00:01", target_date, target_period, 120.0), # Just after cutoff
        ])

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_no_future_leakage(self):
        """
        Ensure that a forecast published even 1 second after the decision cutoff
        is NOT selected.
        """
        decision_time = "2026-01-14T11:00:00"
        selected = self.selector.select_forecast("2026-01-15", 17, decision_time)
        
        self.assertEqual(selected, 110.0, "Should select the forecast published AT the cutoff, not AFTER.")
        self.assertNotEqual(selected, 120.0, "FUTURE LEAKAGE DETECTED: Forecast published after cutoff was selected.")

    def test_empty_forecasts(self):
        """
        Ensure it returns None if no forecasts exist before the cutoff.
        """
        decision_time = "2026-01-13T00:00:00"
        selected = self.selector.select_forecast("2026-01-15", 17, decision_time)
        self.assertIsNone(selected)

if __name__ == "__main__":
    unittest.main()
