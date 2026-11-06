import json

from google import genai
from google.genai import types

from config.settings import Settings
from models.product import ProductCard, ProductInput
from prompts.product_card_prompt import SYSTEM_PROMPT


class GeminiServiceError(RuntimeError):
    pass


class GeminiService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def generate(self, product: ProductInput, extracted_text: str | None = None) -> ProductCard:
        if not self.settings.gemini_api_key or not self.settings.gemini_model:
            raise GeminiServiceError("Укажите GEMINI_API_KEY и GEMINI_MODEL в локальном файле .env.")
        payload = product.model_dump(mode="json")
        if extracted_text:
            payload["url_extracted_text"] = extracted_text
        try:
            client = genai.Client(api_key=self.settings.gemini_api_key)
            response = client.models.generate_content(
                model=self.settings.gemini_model,
                contents=json.dumps(payload, ensure_ascii=False),
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=ProductCard,
                    temperature=0,
                ),
            )
            if not response.text:
                raise GeminiServiceError("Gemini вернул пустой ответ.")
            return ProductCard.model_validate_json(response.text)
        except GeminiServiceError:
            raise
        except Exception as exc:
            raise GeminiServiceError("Не удалось сформировать карточку. Проверьте ключ, модель и соединение.") from exc
