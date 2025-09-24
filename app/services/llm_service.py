"""
Сервис для работы с LLM (OpenAI GPT)
Анализ данных о рейсах и ответы на вопросы пользователей
"""

import json

from openai import AsyncOpenAI

from .flight_api import FlightData


class LLMService:
    """Сервис для анализа данных о рейсах с помощью LLM"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)

    async def analyze_flight_data(
        self, question: str, flight_data: list[FlightData], airport_code: str
    ) -> str:
        """
        Анализ данных о рейсах и ответ на вопрос пользователя

        Args:
            question: Вопрос пользователя
            flight_data: Данные о рейсах
            airport_code: Код аэропорта

        Returns:
            Ответ на вопрос пользователя
        """
        # Подготавливаем данные для LLM
        flights_summary = self._prepare_flight_summary(flight_data, airport_code)

        # Системное сообщение с инструкциями
        system_message = f"""
Ты - эксперт по авиационным данным. Твоя задача - анализировать данные о рейсах,
прилетающих в аэропорт {airport_code}, и отвечать на вопросы пользователей.

Важные правила:
1. Используй только предоставленные данные о рейсах
2. Отвечай точно и конкретно на заданный вопрос
3. Если данных недостаточно для ответа, укажи это
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
{flights_summary}
"""

        # Проверяем, используется ли мок-ключ
        if self.client.api_key == "mock_openai_key":
            return self._generate_mock_response(question, flight_data, airport_code)

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
                ],
                max_tokens=1000,
                temperature=0.1,
            )

            return response.choices[0].message.content or "Не удалось получить ответ"

        except Exception as e:
            return f"Ошибка при обработке запроса: {e}"

    def _prepare_flight_summary(
        self, flight_data: list[FlightData], airport_code: str
    ) -> str:
        """
        Подготовка краткой сводки данных о рейсах для LLM

        Args:
            flight_data: Данные о рейсах
            airport_code: Код аэропорта

        Returns:
            JSON строка с данными о рейсах
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

    def _generate_mock_response(
        self, question: str, flight_data: list[FlightData], airport_code: str
    ) -> str:
        """
        Генерация мок-ответа для демонстрации без OpenAI API

        Args:
            question: Вопрос пользователя
            flight_data: Данные о рейсах
            airport_code: Код аэропорта

        Returns:
            Мок-ответ на вопрос
        """
        total_flights = len(flight_data)
        countries = {flight.departure_country for flight in flight_data}
        airlines = {flight.airline for flight in flight_data}

        # Генерируем базовый ответ на основе статистики
        if "сколько" in question.lower() or "количество" in question.lower():
            if "стран" in question.lower():
                return f"В аэропорт {airport_code} прилетают рейсы из {len(countries)} стран: {', '.join(sorted(countries)[:5])}{'...' if len(countries) > 5 else ''}."
            elif "рейс" in question.lower():
                return f"Всего проанализировано {total_flights} рейсов в аэропорт {airport_code}."
        elif "авиакомпани" in question.lower():
            top_airlines = list(airlines)[:3]
            return f"Основные авиакомпании, выполняющие рейсы в {airport_code}: {', '.join(top_airlines)}."
        elif "стран" in question.lower():
            top_countries = list(countries)[:5]
            return f"Основные страны отправления рейсов в {airport_code}: {', '.join(top_countries)}."
        else:
            return f"""
📊 Анализ данных для аэропорта {airport_code}:

• Всего рейсов: {total_flights}
• Стран отправления: {len(countries)}
• Авиакомпаний: {len(airlines)}
• Основные страны: {", ".join(list(countries)[:3])}

*Примечание: Это демонстрационный ответ. Для полного анализа с помощью ИИ настройте OpenAI API ключ.*
"""

    async def get_sample_questions(self, airport_code: str) -> list[str]:
        """
        Генерация примеров вопросов для аэропорта

        Args:
            airport_code: Код аэропорта

        Returns:
            Список примеров вопросов
        """
        airport_names = {
            "DXB": "Dubai International",
            "LHR": "London Heathrow",
            "CDG": "Charles de Gaulle (Paris)",
            "SIN": "Singapore Changi",
            "HKG": "Hong Kong International",
            "AMS": "Amsterdam Schiphol",
        }

        airport_name = airport_names.get(airport_code, airport_code)

        return [
            f"Сколько рейсов прилетело в {airport_name} из Германии?",
            f"Какие авиакомпании чаще всего летают в {airport_name}?",
            f"Из каких стран больше всего рейсов в {airport_name}?",
            f"Сколько всего стран представлено в рейсах в {airport_name}?",
            f"Какие города чаще всего связаны с {airport_name}?",
        ]
