import requests
import time
from typing import List, Dict, Any, Optional

class ElexonClient:
    # Updated BASE_URL to the one provided in the working curl
    BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1"

    def __init__(self):
        self._cache = {}
        self._cache_ttl = 3600  # Cache for 1 hour

    def _get_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/plain",
        }

    def fetch_fuel_hh(self, date_from: str, date_to: str) -> List[Dict[str, Any]]:
        cache_key = f"fuel_{date_from}_{date_to}"
        if cache_key in self._cache:
            timestamp, data = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return data

        endpoint = f"{self.BASE_URL}/datasets/FUELHH/stream"
        params = {
            "settlementDateFrom": date_from,
            "settlementDateTo": date_to,
            "fuelType": "WIND"
        }
        try:
            response = requests.get(endpoint, params=params, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            if not response.text:
                return []
            data = response.json() if isinstance(response.json(), list) else response.json().get("data", [])
            self._cache[cache_key] = (time.time(), data)
            return data
        except Exception as e:
            print(f"Request failed for FUELHH: {e}")
            return []

    def fetch_wind_for(self, publish_from: str, publish_to: str) -> List[Dict[str, Any]]:
        cache_key = f"wind_{publish_from}_{publish_to}"
        if cache_key in self._cache:
            timestamp, data = self._cache[cache_key]
            if time.time() - timestamp < self._cache_ttl:
                return data

        endpoint = f"{self.BASE_URL}/datasets/WINDFOR/stream"
        params = {
            "publishDateTimeFrom": publish_from,
            "publishDateTimeTo": publish_to,
        }
        try:
            response = requests.get(endpoint, params=params, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            if not response.text:
                return []
            data = response.json() if isinstance(response.json(), list) else response.json().get("data", [])
            self._cache[cache_key] = (time.time(), data)
            return data
        except Exception as e:
            print(f"Request failed for WINDFOR: {e}")
            return []
