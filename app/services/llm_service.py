from typing import Any

from openai import AsyncOpenAI


class LLMService:
    """Сервис для анализа данных о рейсах с помощью LLM"""

    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key, base_url="https://api.perplexity.ai")

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
                model="sonar",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": question},
                ],
            )
            return response.choices[0].message.content or "Не удалось получить ответ"

        except Exception as e:
            return f"Ошибка при обработке запроса: {e}"
