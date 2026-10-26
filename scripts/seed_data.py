from src.db.database import Database
from datetime import datetime, timedelta

def seed():
    db = Database()
    
    # Target Interval: 2026-01-15, Period 17 (08:00-08:30)
    target_date = "2026-01-15"
    target_period = 17
    
    # Actuals
    fuel_records = [
        (target_date, target_period, "NUCLEAR", 1200.0, "2026-01-15T09:00:00"),
        (target_date, target_period, "WIND", 800.0, "2026-01-15T09:00:00"),
        (target_date, target_period, "GAS", 500.0, "2026-01-15T09:00:00"),
    ]
    db.insert_fuel_hh(fuel_records)
    
    # Forecasts (Multiple forecasts for the same interval)
    # Decision Cutoff: 2026-01-14T11:00:00
    wind_records = [
        ("2026-01-13T12:00:00", target_date, target_period, 700.0), # Early forecast
        ("2026-01-14T08:00:00", target_date, target_period, 750.0), # Close to cutoff
        ("2026-01-14T10:55:00", target_date, target_period, 820.0), # Right before cutoff (Expected)
        ("2026-01-14T11:05:00", target_date, target_period, 850.0), # After cutoff (Leakage!)
        ("2026-01-14T15:00:00", target_date, target_period, 810.0), # Late forecast
    ]
    db.insert_wind_for(wind_records)
    
    print("Seed data inserted successfully.")

if __name__ == "__main__":
    seed()
