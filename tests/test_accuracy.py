import pytest
import numpy as np
from src.core.accuracy import AccuracyCalculator, AccuracyMetrics

def test_accuracy_calculations():
    actuals = [100.0, 200.0, 300.0]
    forecasts = [110.0, 190.0, 300.0]
    # Errors: -10, 10, 0
    # Abs Errors: 10, 10, 0
    
    metrics = AccuracyCalculator.calculate(actuals, forecasts)
    
    assert metrics.mae == (10 + 10 + 0) / 3
    assert metrics.bias == (-10 + 10 + 0) / 3
    assert metrics.rmse == np.sqrt((100 + 100 + 0) / 3)
    assert metrics.wape == (10 + 10 + 0) / (100 + 200 + 300)
    assert metrics.sample_count == 3

def test_accuracy_missing_data():
    actuals = [100.0, None, 300.0]
    forecasts = [110.0, 200.0, None]
    # Only pair [0] is valid
    
    metrics = AccuracyCalculator.calculate(actuals, forecasts)
    assert metrics.sample_count == 1
    assert metrics.mae == 10.0

def test_accuracy_no_data():
    actuals = [None, None]
    forecasts = [100.0, 200.0]
    metrics = AccuracyCalculator.calculate(actuals, forecasts)
    assert metrics is None
