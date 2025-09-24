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

    async def get_airport_arrivals(self, airport_code: str) -> list[FlightData]:
        """
        Получение данных о прилетающих рейсах в аэропорт
        """

        if airport_code not in [airport.code for airport in config.SUPPORTED_AIRPORTS]:
            raise ValueError(f"Неподдерживаемый аэропорт: {airport_code}")

        flights = []
        try:
            url = f"{self.base_url}/schedule/{self.api_key}"
            params = {"mode": "arrivals", "day": 1, "iata": airport_code}
            response = await self.client.get(url, params=params)

            if response.status_code == 200:
                data = response.json()

                # FlightRadar24 API structure: airport.pluginData.schedule.departures.data
                airport_data = data.get("airport", {})
                plugin_data = airport_data.get("pluginData", {})
                schedule = plugin_data.get("schedule", {})
                departures = schedule.get("departures", {})
                flight_data = departures.get("data", [])

                for flight_info in flight_data:
                    flight = self._parse_flight_data(flight_info, airport_code)
                    if flight:
                        flights.append(flight)

        except httpx.HTTPError:
            return []
        return flights

    def _parse_flight_data(
        self, flight_info: dict[str, Any], departure_airport: str
    ) -> FlightData | None:
        """
        Парсинг данных о рейсе из ответа FlightRadar24 API
        """
        try:
            # Извлекаем информацию о рейсе из FlightRadar24 структуры
            flight_data = flight_info.get("flight", {})
            identification = flight_data.get("identification", {})
            flight_number = identification.get("number", {}).get("default", "N/A")

            # Информация об авиакомпании
            airline_data = flight_data.get("airline", {})
            airline = airline_data.get("name", "N/A")

            # Информация об аэропорте назначения
            airport_data = flight_data.get("airport", {})
            destination = airport_data.get("destination", {})
            arrival_airport = destination.get("code", {}).get("iata", "N/A")

            # Позиция аэропорта назначения
            destination_position = destination.get("position", {})
            destination_country_data = destination_position.get("country", {})
            arrival_country = destination_country_data.get("name", "Unknown")
            destination_region = destination_position.get("region", {})
            arrival_city = destination_region.get("city", "Unknown")

            # Время рейса
            time_data = flight_data.get("time", {})
            scheduled_data = time_data.get("scheduled", {})
            real_data = time_data.get("real", {})

            # Парсим время отправления (используем timestamp)
            scheduled_departure = scheduled_data.get("departure")
            real_departure = real_data.get("departure")

            scheduled_time = (
                self._parse_timestamp(scheduled_departure)
                if scheduled_departure
                else datetime.now()
            )
            actual_time = (
                self._parse_timestamp(real_departure) if real_departure else None
            )

            # Статус рейса
            status_data = flight_data.get("status", {})
            status = status_data.get("text", "Unknown")

            return FlightData(
                flight_number=flight_number,
                airline=airline,
                departure_airport=departure_airport,
                departure_country=self.supported_airports[departure_airport]["country"],
                departure_city=self.supported_airports[departure_airport]["city"],
                arrival_airport=arrival_airport,
                arrival_country=arrival_country,
                arrival_city=arrival_city,
                scheduled_time=scheduled_time,
                actual_time=actual_time,
                status=status,
            )
        except Exception:
            # Возвращаем None при ошибке парсинга
            return None

    def _parse_datetime(self, datetime_str: str) -> datetime:
        """
        Парсинг строки даты/времени в объект datetime

        Args:
            datetime_str: Строка с датой и временем

        Returns:
            Объект datetime
        """
        # Пробуем различные форматы
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue

        # Если не удалось распарсить, возвращаем текущее время
        return datetime.now()

    def _parse_timestamp(self, timestamp: int) -> datetime:
        """
        Парсинг Unix timestamp в объект datetime

        Args:
            timestamp: Unix timestamp

        Returns:
            Объект datetime
        """
        try:
            return datetime.fromtimestamp(timestamp)
        except (ValueError, TypeError):
            return datetime.now()

    async def get_mock_data(self, airport_code: str) -> list[FlightData]:
        """
        Генерация тестовых данных для демонстрации
        Используется когда нет доступа к реальному API

        Args:
            airport_code: Код аэропорта

        Returns:
            Список тестовых данных о рейсах
        """
        mock_flights = []

        # Примерные страны и города отправления
        origins = [
            {"country": "Germany", "city": "Frankfurt", "airport": "FRA"},
            {"country": "France", "city": "Paris", "airport": "CDG"},
            {"country": "USA", "city": "New York", "airport": "JFK"},
            {"country": "Japan", "city": "Tokyo", "airport": "NRT"},
            {"country": "Australia", "city": "Sydney", "airport": "SYD"},
            {"country": "India", "city": "Mumbai", "airport": "BOM"},
            {"country": "China", "city": "Beijing", "airport": "PEK"},
            {"country": "Brazil", "city": "São Paulo", "airport": "GRU"},
            {"country": "Canada", "city": "Toronto", "airport": "YYZ"},
            {"country": "South Korea", "city": "Seoul", "airport": "ICN"},
        ]

        airlines = [
            "Lufthansa",
            "Air France",
            "British Airways",
            "Emirates",
            "Singapore Airlines",
            "Cathay Pacific",
            "KLM",
            "Delta",
            "United",
            "Qatar Airways",
        ]

        for i, origin in enumerate(origins * 3):  # Увеличиваем количество рейсов
            flight = FlightData(
                flight_number=f"{airlines[i % len(airlines)][:2]}{100 + i}",
                airline=airlines[i % len(airlines)],
                departure_airport=origin["airport"],
                departure_country=origin["country"],
                departure_city=origin["city"],
                arrival_airport=airport_code,
                arrival_country=self.supported_airports[airport_code]["country"],
                arrival_city=self.supported_airports[airport_code]["city"],
                scheduled_time=datetime.now() - timedelta(hours=i % 24),
                actual_time=datetime.now() - timedelta(hours=i % 24, minutes=15),
                status="Landed" if i % 3 == 0 else "On Time",
            )
            mock_flights.append(flight)

        return mock_flights

    async def close(self):
        """Закрытие HTTP клиента"""
        await self.client.aclose()
