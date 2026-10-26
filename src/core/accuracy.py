import numpy as np
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class AccuracyMetrics:
    mae: float
    rmse: float
    bias: float
    wape: float
    p90_abs_error: float
    coverage: float
    sample_count: int
    missing_count: int

class AccuracyCalculator:
    @staticmethod
    def calculate(actuals: List[float], forecasts: List[float]) -> Optional[AccuracyMetrics]:
        """
        Calculates accuracy metrics between actuals and forecasts.
        Actuals and forecasts must be aligned by index.
        """
        # Filter out pairs where either is None
        pairs = [(a, f) for a, f in zip(actuals, forecasts) if a is not None and f is not None]
        
        sample_count = len(pairs)
        if sample_count == 0:
            return None

        actuals_arr = np.array([p[0] for p in pairs])
        forecasts_arr = np.array([p[1] for p in pairs])
        
        errors = actuals_arr - forecasts_arr
        abs_errors = np.abs(errors)
        
        mae = np.mean(abs_errors)
        rmse = np.sqrt(np.mean(errors**2))
        bias = np.mean(errors)
        
        # WAPE = sum(|actual - forecast|) / sum(|actual|)
        sum_actuals = np.sum(np.abs(actuals_arr))
        wape = np.sum(abs_errors) / sum_actuals if sum_actuals != 0 else 0.0
        
        p90_abs_error = np.percentile(abs_errors, 90)
        
        # Coverage calculation happens at a higher level usually, 
        # but we can pass it in or calculate it relative to expected total.
        # For this specific function, we just report what we have.
        
        return AccuracyMetrics(
            mae=float(mae),
            rmse=float(rmse),
            bias=float(bias),
            wape=float(wape),
            p90_abs_error=float(p90_abs_error),
            coverage=0.0, # To be set by the service
            sample_count=sample_count,
            missing_count=0 # To be set by the service
        )
