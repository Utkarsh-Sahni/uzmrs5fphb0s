from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple, NamedTuple

class HourlyActual(NamedTuple):
    timestamp: datetime
    value_mw: float
    is_complete: bool

def aggregate_fuel_hh_to_hourly(fuel_data: List[Dict]) -> Dict[datetime, HourlyActual]:
    """
    Aggregates half-hourly FUELHH actuals into hourly averages.

    Requirement:
    - Both half-hourly observations for a complete hourly actual value.
    - Otherwise mark that hour as incomplete.
    """
    hourly_bins: Dict[datetime, List[float]] = {}

    for item in fuel_data:
        start_time_str = item.get("startTime")
        if not start_time_str:
            continue

        # Parse ISO timestamp to UTC datetime
        dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))

        # Floor to the start of the hour
        hour_start = dt.replace(minute=0, second=0, microsecond=0)

        if item.get("fuelType") == "WIND":
            val = float(item.get("generation", 0))
            if hour_start not in hourly_bins:
                hourly_bins[hour_start] = []
            hourly_bins[hour_start].append(val)

    results = {}
    # We expect 24 hours in a day.
    # This function can be called for a single day or multiple.
    for hour, values in hourly_bins.items():
        if len(values) == 2:
            avg_val = sum(values) / 2.0
            results[hour] = HourlyActual(timestamp=hour, value_mw=avg_val, is_complete=True)
        else:
            # Incomplete hour: can't accurately average.
            # We store it as incomplete.
            results[hour] = HourlyActual(timestamp=hour, value_mw=sum(values)/len(values) if values else 0.0, is_complete=False)

    return results
