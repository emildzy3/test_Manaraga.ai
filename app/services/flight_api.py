from datetime import datetime, timedelta
from typing import Any

import httpx

from app.core import config


class FlightAPIClient:
    """Клиент для работы с FlightAPI.io"""

    def __init__(self, api_key: str, cache_ttl_minutes: int = 15):
        self.api_key = api_key
        self.base_url = "https://api.flightapi.io"
        self.client = httpx.AsyncClient(
            timeout=5,
            headers={
                "Content-Type": "application/json",
            },
        )
        self.cache_ttl = timedelta(minutes=cache_ttl_minutes)
        self.cache: dict[str, dict] = {}

    async def get_airport_arrivals(self, airport_code: str) -> dict[str, Any]:
        """
        Получение данных о рейсах в аэропорт с кешированием
        """

        if airport_code not in [airport.code for airport in config.SUPPORTED_AIRPORTS]:
            raise ValueError(f"Неподдерживаемый аэропорт: {airport_code}")

        # Проверяем кеш
        cache_key = f"arrivals_{airport_code}"
        if cache_key in self.cache and self._is_cache_valid(self.cache[cache_key]):
            return self.cache[cache_key]["data"]

        result_info = {"airport_info": "", "arrivals": [], "departures": []}
        for fly_mode in ["arrivals", "departures"]:
            try:
                url = f"{self.base_url}/schedule/{self.api_key}"
                params = {"mode": fly_mode, "day": 1, "iata": airport_code}
                response = await self.client.get(url, params=params)
                if response.status_code == 200:
                    data = response.json()
                    result_info[fly_mode] = data["airport"]["pluginData"]
            except httpx.HTTPError:
                continue
        self.cache[cache_key] = {"data": result_info, "cached_at": datetime.now()}
        return result_info

    def _is_cache_valid(self, cache_entry: dict) -> bool:
        cached_at = cache_entry.get("cached_at")
        if not cached_at:
            return False
        return datetime.now() - cached_at < self.cache_ttl
