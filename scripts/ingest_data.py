import argparse
from datetime import datetime, timedelta
from src.ingestion.elexon_client import ElexonClient
from src.db.database import Database
import os

def ingest_fuel_hh(client: ElexonClient, db: Database, start_date: str, end_date: str):
    print(f"Ingesting FUELHH from {start_date} to {end_date}...")
    data = client.fetch_fuel_hh(start_date, end_date)
    
    records = []
    for item in data:
        # According to documentation for /stream:
        # "startTime" is the target time, "generation" is power
        # We need to extract date and period from startTime
        try:
            start_time_str = item.get("startTime")
            if not start_time_str: continue
            
            dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            date_val = dt.strftime("%Y-%m-%d")
            
            # Settlement period: 1-48. Period 1 starts at 00:00.
            # Period = (hour * 2) + (1 if minute >= 30 else 0) + 1
            period = (dt.hour * 2) + (1 if dt.minute >= 30 else 0) + 1
            
            # Only keep WIND fuel type
            if item.get("fuelType") == "WIND":
                records.append((
                    date_val,
                    period,
                    "WIND",
                    float(item.get("generation", 0)),
                    dt.isoformat()
                ))
        except Exception as e:
            continue
    
    db.insert_fuel_hh(records)
    print(f"Inserted {len(records)} FUELHH records.")

def ingest_wind_for(client: ElexonClient, db: Database, start_publish: str, end_publish: str):
    print(f"Ingesting WINDFOR from {start_publish} to {end_publish}...")
    data = client.fetch_wind_for(start_publish, end_publish)
    
    records = []
    for item in data:
        # According to documentation for /stream:
        # "publishTime", "startTime", "generation"
        try:
            publish_time = item.get("publishTime")
            start_time_str = item.get("startTime")
            if not publish_time or not start_time_str: continue
            
            dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00"))
            date_val = dt.strftime("%Y-%m-%d")
            period = (dt.hour * 2) + (1 if dt.minute >= 30 else 0) + 1
            
            records.append((
                publish_time,
                date_val,
                period,
                float(item.get("generation", 0))
            ))
        except Exception as e:
            continue
    
    db.insert_wind_for(records)
    print(f"Inserted {len(records)} WINDFOR records.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fuel-start", required=True)
    parser.add_argument("--fuel-end", required=True)
    parser.add_argument("--wind-start", required=True)
    parser.add_argument("--wind-end", required=True)
    args = parser.parse_args()

    client = ElexonClient()
    db = Database()

    ingest_fuel_hh(client, db, args.fuel_start, args.fuel_end)
    ingest_wind_for(client, db, args.wind_start, args.wind_end)
