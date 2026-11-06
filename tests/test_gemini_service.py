from unittest.mock import Mock, patch

from config.settings import Settings
from models.product import ProductInput
from services.gemini_service import GeminiService


@patch("services.gemini_service.genai.Client")
def test_gemini_response_is_validated(mock_client):
    mock_client.return_value.models.generate_content.return_value.text = '{"seo_title":"Товар","seo_description":"Данных нет","specifications":[],"search_queries":[],"sales_block":{"target_audience":"Данных нет","tasks":"Данных нет","applications":"Данных нет"},"warnings":[],"sources":[]}'
    service = GeminiService(Settings("key", "model", 15))
    assert service.generate(ProductInput(product_name="Товар")).seo_title == "Товар"
