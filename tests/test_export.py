from models.product import ProductCard, SpecificationOutput
from utils.export import card_to_json, card_to_markdown, card_to_text


def test_exports_preserve_source_values():
    card = ProductCard(specifications=[SpecificationOutput(parameter="Ток", value="0,5", unit="А", status="подтверждено")])
    assert '"value": "0,5"' in card_to_json(card)
    assert "| Ток | 0,5 | А" in card_to_markdown(card)
    assert "0,5" in card_to_text(card)
