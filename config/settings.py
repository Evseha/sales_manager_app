from dataclasses import dataclass
import os

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None
    gemini_model: str | None
    request_timeout: int


def get_settings() -> Settings:
    load_dotenv()
    timeout = os.getenv("REQUEST_TIMEOUT", "15")
    try:
        timeout_value = max(1, int(timeout))
    except ValueError:
        timeout_value = 15
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
        gemini_model=os.getenv("GEMINI_MODEL") or None,
        request_timeout=timeout_value,
    )
