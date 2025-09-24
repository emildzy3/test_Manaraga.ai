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

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.flightapi.io"
        self.client = httpx.AsyncClient(
            timeout=5,
            headers={
                "Content-Type": "application/json",
            },
        )

        # Создаем словарь поддерживаемых аэропортов для быстрого доступа
        self.supported_airports = {
            airport.code: {
                "name": airport.name,
                "country": airport.country,
                "city": airport.city,
            }
            for airport in config.SUPPORTED_AIRPORTS
        }

    async def get_airport_arrivals(self, airport_code: str) -> dict[str, Any]:
        """
        Получение данных о рейсах в аэропорт
        """

        if airport_code not in [airport.code for airport in config.SUPPORTED_AIRPORTS]:
            raise ValueError(f"Неподдерживаемый аэропорт: {airport_code}")
        result_info = {"airport_info": "", "arrivals": [], "departures": []}
        for fly_mode in ["arrivals", "departures"]:
            try:
                url = f"{self.base_url}/schedule/{self.api_key}"
                params = {"mode": fly_mode, "day": 1, "iata": airport_code}
                response = await self.client.get(url, params=params)

                if response.status_code == 200:
                    data = response.json()
            except httpx.HTTPError:
                continue
            result_info[fly_mode] = data
        return result_info
