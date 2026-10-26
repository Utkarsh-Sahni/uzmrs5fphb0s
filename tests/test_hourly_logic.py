import pytest
from datetime import datetime, timedelta
from src.core.data_utils import aggregate_fuel_hh_to_hourly, HourlyActual
from src.core.accuracy import AccuracyCalculator
from src.api.main import process_forecast_as_of_refined

def test_aggregation_complete():
    # Mock data: 2 half-hours for hour 0, 1 for hour 1
    data = [
        {"startTime": "2023-01-01T00:00:00Z", "fuelType": "WIND", "generation": 100},
        {"startTime": "2023-01-01T00:30:00Z", "fuelType": "WIND", "generation": 200},
        {"startTime": "2023-01-01T01:00:00Z", "fuelType": "WIND", "generation": 150},
    ]
    results = aggregate_fuel_hh_to_hourly(data)

    h0 = datetime.fromisoformat("2023-01-01T00:00:00+00:00")
    h1 = datetime.fromisoformat("2023-01-01T01:00:00+00:00")

    assert results[h0].value_mw == 150.0
    assert results[h0].is_complete is True
    assert results[h1].is_complete is False

def test_forecast_selection_cutoff():
    forecasts = [
        {"startTime": "2023-01-01T00:00:00Z", "publishTime": "2022-12-31T12:00:00Z", "generation": 100},
        {"startTime": "2023-01-01T00:00:00Z", "publishTime": "2023-01-01T00:00:00Z", "generation": 110},
        {"startTime": "2023-01-01T00:00:00Z", "publishTime": "2023-01-01T01:00:00Z", "generation": 120},
    ]
    # Cutoff at 00:30:00Z
    val, pub = process_forecast_as_of_refined(forecasts, "2023-01-01", 1, "2023-01-01T00:30:00Z")
    assert val == 110
    assert pub == "2023-01-01T00:00:00Z"

def test_forecast_selection_retrospective():
    # startTime is 00:00, but publishTime is 01:00 (retrospective)
    forecasts = [
        {"startTime": "2023-01-01T00:00:00Z", "publishTime": "2023-01-01T01:00:00Z", "generation": 100},
    ]
    val, pub = process_forecast_as_of_refined(forecasts, "2023-01-01", 1, "2023-01-01T02:00:00Z")
    assert val is None

def test_accuracy_metrics():
    actuals = [100.0, 200.0, None]
    forecasts = [110.0, 190.0, 150.0]
    # Total expected 3
    metrics = AccuracyCalculator.calculate(actuals, forecasts, total_expected=3)

    assert metrics.sample_count == 2
    assert metrics.mae == 10.0
    assert metrics.coverage == 2/3
    assert metrics.missing_count == 1
