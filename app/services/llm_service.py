"""
Сервис для работы с LLM (OpenAI GPT)
Анализ данных о рейсах и ответы на вопросы пользователей
"""

import json
from typing import Any

from openai import AsyncOpenAI

from .flight_api import FlightData


class LLMService:
    """Сервис для анализа данных о рейсах с помощью LLM"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def analyze_flight_data(
        self,
        question: str,
        flight_data: dict[str, Any],
        airport_code: str,
    ) -> str:
        """
        Анализ данных о рейсах и ответ на вопрос пользователя
        """

        system_message = f"""
            Ты - эксперт по авиационным данным. Твоя задача - анализировать данные о рейсах,
            прилетающих в аэропорт {airport_code}, и отвечать на вопросы пользователей.

            Важные правила:
            1. Используй только предоставленные данные о рейсах
            2. Отвечай точно и конкретно на заданный вопрос
            4. Приводи числовые данные где это уместно
            5. Отвечай на русском языке
            6. Если в вопросе упоминается несколько аэропортов, фокусируйся только на {airport_code}

            Доступные данные включают:
            - Страны и города отправления рейсов
            - Авиакомпании
            - Номера рейсов
            - Время прилета
            - Статус рейсов

            Данные о рейсах в формате JSON:
            {flight_data}
        """

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
                ],
            )
            return response.choices[0].message.content or "Не удалось получить ответ"

        except Exception as e:
            return f"Ошибка при обработке запроса: {e}"

    def _prepare_flight_summary(
        self,
        flight_data: list[FlightData],
        airport_code: str,
    ) -> str:
        """
        Подготовка краткой сводки данных о рейсах для LLM
        """

        summary_data = {
            "airport": airport_code,
            "total_flights": len(flight_data),
            "countries": {},
            "cities": {},
            "airlines": {},
            "flights": [],
        }

        # Подсчитываем статистику по странам, городам и авиакомпаниям
        for flight in flight_data:
            # Страны
            country = flight.departure_country
            if country in summary_data["countries"]:
                summary_data["countries"][country] += 1
            else:
                summary_data["countries"][country] = 1

            # Города
            city = flight.departure_city
            if city in summary_data["cities"]:
                summary_data["cities"][city] += 1
            else:
                summary_data["cities"][city] = 1

            # Авиакомпании
            airline = flight.airline
            if airline in summary_data["airlines"]:
                summary_data["airlines"][airline] += 1
            else:
                summary_data["airlines"][airline] = 1

            # Добавляем данные о рейсе
            flight_info = {
                "flight_number": flight.flight_number,
                "airline": flight.airline,
                "from_country": flight.departure_country,
                "from_city": flight.departure_city,
                "from_airport": flight.departure_airport,
                "scheduled_time": flight.scheduled_time.isoformat(),
                "status": flight.status,
            }
            summary_data["flights"].append(flight_info)

        return json.dumps(summary_data, ensure_ascii=False, indent=2)
