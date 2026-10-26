import asyncio
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
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
    actual: Optional[float]
    forecast: Optional[float]
    error: Optional[float]
    publish_time: Optional[str]

def process_forecast_as_of(forecasts: List[Dict], target_date: str, period: int, decision_cutoff: str):
    best_forecast = None
    latest_publish_time = None
    for f in forecasts:
        start_time = f.get("startTime")
        if not start_time: continue
        dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        if dt.strftime("%Y-%m-%d") != target_date: continue
        p = (dt.hour * 2) + (1 if dt.minute >= 30 else 0) + 1
        if p != period: continue
        publish_time = f.get("publishTime")
        if not publish_time: continue
        if publish_time <= decision_cutoff:
            if latest_publish_time is None or publish_time > latest_publish_time:
                latest_publish_time = publish_time
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

    actuals = []
    forecasts = []
    missing_count = 0
    periods = []
    fuel_map = {}
    for item in fuel_data:
        start_time = item.get("startTime")
        if not start_time: continue
        dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        p = (dt.hour * 2) + (1 if dt.minute >= 30 else 0) + 1
        if item.get("fuelType") == "WIND":
            fuel_map[p] = float(item.get("generation", 0))
            periods.append(p)

    periods = sorted(list(set(periods)))

    for period in periods:
        wind_actual = fuel_map.get(period)
        forecast_val, _ = process_forecast_as_of(wind_forecasts, date, period, decision_cutoff)
        if wind_actual is not None and forecast_val is not None:
            actuals.append(wind_actual)
            forecasts.append(forecast_val)
        else:
            missing_count += 1
            actuals.append(wind_actual)
            forecasts.append(None)

    metrics = AccuracyCalculator.calculate(actuals, forecasts)
    if not metrics:
        raise HTTPException(status_code=404, detail="Insufficient data to calculate accuracy.")

    coverage = (len(periods) - missing_count) / len(periods) if periods else 0

    return AccuracyResponse(
        mae=metrics.mae,
        rmse=metrics.rmse,
        bias=metrics.bias,
        wape=metrics.wape,
        p90_abs_error=metrics.p90_abs_error,
        coverage=coverage,
        sample_count=metrics.sample_count,
        missing_count=missing_count,
        metadata={
            "decision_cutoff": decision_cutoff,
            "target_date": date,
            "units": "MW",
            "target_intervals": len(periods),
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

    fuel_map = {}
    periods = []
    for item in fuel_data:
        start_time = item.get("startTime")
        if not start_time: continue
        dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        p = (dt.hour * 2) + (1 if dt.minute >= 30 else 0) + 1
        if item.get("fuelType") == "WIND":
            fuel_map[p] = float(item.get("generation", 0))
            periods.append(p)

    periods = sorted(list(set(periods)))
    errors = []

    for period in periods:
        wind_actual = fuel_map.get(period)
        forecast_val, publish_time = process_forecast_as_of(wind_forecasts, date, period, decision_cutoff)
        error_val = (wind_actual - forecast_val) if (wind_actual is not None and forecast_val is not None) else None
        errors.append(IntervalError(
            period=period,
            actual=wind_actual,
            forecast=forecast_val,
            error=error_val,
            publish_time=publish_time
        ))

    return errors
