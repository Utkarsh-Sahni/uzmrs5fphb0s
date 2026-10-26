import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from src.ingestion.elexon_client import ElexonClient
from src.core.accuracy import AccuracyCalculator, AccuracyMetrics

app = FastAPI(title="GridBrick Accuracy API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencies
client = ElexonClient()

class AccuracyResponse(BaseModel):
    mae: float
    rmse: float
    bias: float
    wape: float
    p90_abs_error: float
    coverage: float
    sample_count: int
    missing_count: int
    metadata: Dict[str, Any]

class IntervalError(BaseModel):
    period: int
    target_time: str
    actual: Optional[float]
    forecast: Optional[float]
    error: Optional[float]
    publish_time: Optional[str]

def process_forecast_as_of_refined(forecasts: List[Dict], target_date: str, hour: int, decision_cutoff: str):
    """
    Requirement:
    - Latest available forecast version published before the decision cutoff.
    - Do not select forecasts published after the cutoff.
    - Exclude retrospective forecast targets where startTime < publishTime.
    """
    best_forecast = None
    latest_publish_time = None

    for f in forecasts:
        start_time_str = f.get("startTime")
        publish_time_str = f.get("publishTime")
        if not start_time_str or not publish_time_str:
            continue

        start_dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
        publish_dt = datetime.fromisoformat(publish_time_str.replace("Z", "+00:00"))

        # Filter: target date must match
        if start_dt.strftime("%Y-%m-%d") != target_date:
            continue

        # Filter: target hour must match (1-24)
        if start_dt.hour + 1 != hour:
            continue

        # Requirement 7: Exclude retrospective (startTime < publishTime)
        if start_dt < publish_dt:
            continue

        # Requirement 5 & 6: Latest published before or at cutoff
        if publish_time_str <= decision_cutoff:
            if latest_publish_time is None or publish_time_str > latest_publish_time:
                latest_publish_time = publish_time_str
                best_forecast = float(f.get("generation", 0))

    return best_forecast, latest_publish_time

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.get("/accuracy", response_model=AccuracyResponse)
async def get_accuracy(
    date: str,
    decision_cutoff: str = Query(..., description="ISO format: yyyy-MM-ddTHH:mm:ss")
):
    loop = asyncio.get_event_loop()
    fuel_task = loop.run_in_executor(None, client.fetch_fuel_hh, date, date)

    try:
        cutoff_dt = datetime.fromisoformat(decision_cutoff.replace("Z", "+00:00"))
        start_publish = (cutoff_dt - timedelta(days=7)).isoformat()
    except:
        start_publish = "2022-01-01T00:00:00"

    end_publish = decision_cutoff
    wind_task = loop.run_in_executor(None, client.fetch_wind_for, start_publish, end_publish)
    fuel_data, wind_forecasts = await asyncio.gather(fuel_task, wind_task)

    if not fuel_data:
        raise HTTPException(status_code=404, detail="No actual generation data found for this date.")

    # Requirement 2 & 3: Aggregate half-hourly to hourly
    from src.core.data_utils import aggregate_fuel_hh_to_hourly
    hourly_actuals_map = aggregate_fuel_hh_to_hourly(fuel_data)

    actuals = []
    forecasts = []

    # Target date in UTC
    target_dt = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)

    for hour in range(1, 25):
        # Hour start timestamp
        hour_ts = target_dt + timedelta(hours=hour - 1)

        # 1. Actual: Must be complete (both half-hours present)
        actual_info = hourly_actuals_map.get(hour_ts)
        actual_val = actual_info.value_mw if (actual_info and actual_info.is_complete) else None

        # 2. Forecast: Latest before cutoff, no retrospective
        forecast_val, _ = process_forecast_as_of_refined(wind_forecasts, date, hour, decision_cutoff)

        actuals.append(actual_val)
        forecasts.append(forecast_val)

    metrics = AccuracyCalculator.calculate(actuals, forecasts, total_expected=24)
    if not metrics:
        raise HTTPException(status_code=404, detail="Insufficient data to calculate accuracy.")

    return AccuracyResponse(
        mae=metrics.mae,
        rmse=metrics.rmse,
        bias=metrics.bias,
        wape=metrics.wape,
        p90_abs_error=metrics.p90_abs_error,
        coverage=metrics.coverage,
        sample_count=metrics.sample_count,
        missing_count=metrics.missing_count,
        metadata={
            "decision_cutoff": decision_cutoff,
            "target_date": date,
            "units": "MW",
            "target_intervals": 24,
            "data_source": "Elexon API Direct"
        }
    )

@app.get("/accuracy/intervals", response_model=List[IntervalError])
async def get_interval_errors(
    date: str,
    decision_cutoff: str = Query(..., description="ISO format: yyyy-MM-ddTHH:mm:ss")
):
    loop = asyncio.get_event_loop()
    fuel_task = loop.run_in_executor(None, client.fetch_fuel_hh, date, date)

    try:
        cutoff_dt = datetime.fromisoformat(decision_cutoff.replace("Z", "+00:00"))
        start_publish = (cutoff_dt - timedelta(days=7)).isoformat()
    except:
        start_publish = "2022-01-01T00:00:00"

    end_publish = decision_cutoff
    wind_task = loop.run_in_executor(None, client.fetch_wind_for, start_publish, end_publish)
    fuel_data, wind_forecasts = await asyncio.gather(fuel_task, wind_task)

    if not fuel_data:
        raise HTTPException(status_code=404, detail="No actual data found.")

    # Requirement 2 & 3: Aggregate half-hourly to hourly
    from src.core.data_utils import aggregate_fuel_hh_to_hourly
    hourly_actuals_map = aggregate_fuel_hh_to_hourly(fuel_data)

    target_dt = datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    errors = []

    for hour in range(1, 25):
        hour_ts = target_dt + timedelta(hours=hour - 1)

        # 1. Actual: Must be complete
        actual_info = hourly_actuals_map.get(hour_ts)
        wind_actual = actual_info.value_mw if (actual_info and actual_info.is_complete) else None

        # 2. Forecast: Refined selection
        forecast_val, publish_time = process_forecast_as_of_refined(wind_forecasts, date, hour, decision_cutoff)

        error_val = (wind_actual - forecast_val) if (wind_actual is not None and forecast_val is not None) else None
        errors.append(IntervalError(
            period=hour,
            target_time=hour_ts.strftime("%Y-%m-%d %H:00"),
            actual=wind_actual,
            forecast=forecast_val,
            error=error_val,
            publish_time=publish_time
        ))

    return errors
