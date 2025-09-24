from pydantic import BaseModel
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API ключи
    flight_api_key: str
    perplexity_api_key: str

    # Настройки сервера
    host: str
    port: int
    debug: bool

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


class AirportInfo(BaseModel):
    """Информация об аэропорте"""

    code: str
    name: str
    country: str
    city: str


SUPPORTED_AIRPORTS = [
    AirportInfo(
        code="DXB",
        name="Dubai International",
        country="UAE",
        city="Dubai",
    ),
    AirportInfo(
        code="LHR",
        name="London Heathrow",
        country="UK",
        city="London",
    ),
    AirportInfo(
        code="CDG",
        name="Charles de Gaulle",
        country="France",
        city="Paris",
    ),
    AirportInfo(
        code="SIN",
        name="Singapore Changi",
        country="Singapore",
        city="Singapore",
    ),
    AirportInfo(
        code="HKG",
        name="Hong Kong International",
        country="Hong Kong",
        city="Hong Kong",
    ),
    AirportInfo(
        code="AMS",
        name="Amsterdam Schiphol",
        country="Netherlands",
        city="Amsterdam",
    ),
]


def get_settings() -> Settings:
    return Settings()  # pyright: ignore[reportCallIssue]
