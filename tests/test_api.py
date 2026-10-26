import pytest
from fastapi.testclient import TestClient
from src.api.main import app
from src.db.database import Database
import os
import sqlite3

# We need to override the database instance in the app for testing
from src.api import main

client = TestClient(app)

def setup_module(module):
    test_db_path = "test_api_gridbrick.db"
    # Clear any existing test DB
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    db = Database(test_db_path)
    
    # Override the db in the app
    main.db = db
    main.repo = main.ElexonRepository(db) if hasattr(main, 'ElexonRepository') else None 
    # Wait, main.py defines repo = ElexonRepository(db) at module level.
    # I need to re-initialize it.
    from src.db.repositories import ElexonRepository
    main.repo = ElexonRepository(db)
    
    # Seed data for API tests
    target_date = "2026-01-15"
    target_period = 17
    
    # Actuals
    db.insert_fuel_hh([(target_date, target_period, "WIND", 800.0, "2026-01-15T09:00:00")])
    
    # Forecasts
    db.insert_wind_for([
        ("2026-01-14T10:00:00", target_date, target_period, 700.0),
        ("2026-01-14T11:05:00", target_date, target_period, 900.0),
    ])

def teardown_module(module):
    test_db_path = "test_api_gridbrick.db"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)

def test_get_accuracy_cutoff_filtering():
    # Decision cutoff 11:00:00 should pick the 10:00 forecast (700 MW)
    # Actual is 800 MW. Error = 100 MW.
    response = client.get("/accuracy?date=2026-01-15&decision_cutoff=2026-01-14T11:00:00")
    assert response.status_code == 200
    data = response.json()
    assert data["mae"] == 100.0
    assert data["sample_count"] == 1
    assert data["metadata"]["decision_cutoff"] == "2026-01-14T11:00:00"

def test_get_accuracy_future_leakage():
    # Decision cutoff 11:10:00 should pick the 11:05 forecast (900 MW)
    # Actual is 800 MW. Error = -100 MW. Abs Error = 100 MW.
    response = client.get("/accuracy?date=2026-01-15&decision_cutoff=2026-01-14T11:10:00")
    assert response.status_code == 200
    data = response.json()
    assert data["mae"] == 100.0
    # Note: Bias should be -100 (800 - 900)
    assert data["bias"] == -100.0

def test_get_accuracy_no_data():
    response = client.get("/accuracy?date=2000-01-01&decision_cutoff=2000-01-01T00:00:00")
    assert response.status_code == 404
