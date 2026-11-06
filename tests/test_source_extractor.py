from unittest.mock import Mock, patch

from services.source_extractor import extract_product_page


def test_invalid_url_is_reported_without_request():
    result = extract_product_page("ftp://example.test", 5)
    assert result.error


@patch("services.source_extractor.requests.get")
def test_extracts_visible_page_text(mock_get):
    response = Mock()
    response.text = "<html><head><title>Товар</title><meta name='description' content='Описание'></head><body><p>Данные 24 В</p><script>ignore()</script></body></html>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response
    result = extract_product_page("https://example.test", 5)
    assert result.title == "Товар"
    assert result.meta_description == "Описание"
    assert "Данные 24 В" in result.visible_text
