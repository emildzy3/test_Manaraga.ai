"""
Сервис для работы с FlightAPI.io
Получение данных о расписании рейсов аэропортов
"""

from datetime import datetime, timedelta
from typing import Any

import httpx
from pydantic import BaseModel

from app.core import config


class FlightData(BaseModel):
    """Модель данных о рейсе"""

    flight_number: str
    airline: str
    departure_airport: str
    departure_country: str
    departure_city: str
    arrival_airport: str
    arrival_country: str
    arrival_city: str
    scheduled_time: datetime
    actual_time: datetime | None = None
    status: str


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

        # Создаем словарь поддерживаемых аэропортов для быстрого доступа
        self.supported_airports = {
            airport.code: {
                "name": airport.name,
                "country": airport.country,
                "city": airport.city,
            }
            for airport in config.SUPPORTED_AIRPORTS
        }

    def _is_cache_valid(self, cache_entry: dict) -> bool:
        """Проверка валидности кеша"""
        cached_at = cache_entry.get("cached_at")
        if not cached_at:
            return False
        return datetime.now() - cached_at < self.cache_ttl

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

        # Сохраняем в кеш
        self.cache[cache_key] = {"data": result_info, "cached_at": datetime.now()}

        return result_info
