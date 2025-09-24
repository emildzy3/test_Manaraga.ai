from pathlib import Path
from typing import Any
from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from starlette.templating import _TemplateResponse

from app.core.jinja import get_jinja2_templates
from app.services.flight_api import FlightAPIClient
from app.services.llm_service import LLMService

from app.core.config import SUPPORTED_AIRPORTS, get_settings


router = APIRouter()

settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent.parent
templates = get_jinja2_templates(base_dir=BASE_DIR)

flight_client = FlightAPIClient(settings.flight_api_key)
llm_service = LLMService(settings.openai_api_key)


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> _TemplateResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "airports": SUPPORTED_AIRPORTS,
            "app_name": "Flights by Country",
        },
    )


@router.post("/analyze")
async def analyze_flights(
    airport_code: str = Form(...), question: str = Form(...)
) -> dict[str, Any]:
    """
    Анализ данных о рейсах и ответ на вопрос пользователя
    """
    # Проверяем корректность кода аэропорта
    airport_codes = [airport.code for airport in SUPPORTED_AIRPORTS]
    if airport_code not in airport_codes:
        raise HTTPException(
            status_code=400, detail=f"Неподдерживаемый аэропорт: {airport_code}"
        )

    try:
        # Получаем данные о рейсах
        flight_data = await flight_client.get_airport_arrivals(airport_code)

        # Если нет данных от реального API, используем мок-данные
        if not flight_data:
            flight_data = await flight_client.get_mock_data(airport_code)

        if not flight_data:
            return {
                "success": False,
                "answer": (
                    "Не удалось получить данные о рейсах для выбранного аэропорта."
                ),
            }

        # Анализируем данные с помощью LLM
        answer = await llm_service.analyze_flight_data(
            question, flight_data, airport_code
        )

        return {
            "success": True,
            "answer": answer,
            "flights_count": len(flight_data),
            "airport_code": airport_code,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ошибка при анализе данных: {str(e)}"
        ) from e
