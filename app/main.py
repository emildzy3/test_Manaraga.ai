from fastapi import FastAPI

from .api.routes import router
from .core.config import get_settings

settings = get_settings()

app = FastAPI(
    title="Flights by Country",
    description="Анализ данных о рейсах по странам для различных аэропортов",
)

# Включаем роутеры
app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
