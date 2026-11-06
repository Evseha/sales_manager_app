from models.product import ProductCard, ProductInput, SpecificationInput, SpecificationOutput
from services.validation_service import validate_card


def test_validation_keeps_exact_supported_value_and_unit():
    product = ProductInput(specifications=[SpecificationInput(name="Напряжение", value="24", unit="В", source="паспорт")])
    card = ProductCard(specifications=[SpecificationOutput(parameter="Напряжение", value="24", unit="В", status="подтверждено")])
    validated = validate_card(card, product)
    assert validated.specifications[0].value == "24"
    assert validated.specifications[0].unit == "В"


def test_validation_excludes_unsupported_specification():
    product = ProductInput(product_name="Товар")
    card = ProductCard(specifications=[SpecificationOutput(parameter="Степень защиты", value="IP65", status="подтверждено")])
    validated = validate_card(card, product)
    assert validated.specifications == []
    assert "исключена" in validated.warnings[0]


def test_short_description_is_warning_not_generated_filler():
    product = ProductInput(product_name="Товар")
    card = ProductCard(seo_description="Короткий подтверждённый текст.")
    assert "не дополнялось предположениями" in validate_card(card, product).warnings[0]


def test_conflicting_input_values_require_review():
    product = ProductInput(specifications=[
        SpecificationInput(name="Напряжение", value="24", unit="В"),
        SpecificationInput(name="Напряжение", value="48", unit="В"),
    ])
    card = ProductCard(specifications=[SpecificationOutput(parameter="Напряжение", value="24", unit="В", status="подтверждено")])
    validated = validate_card(card, product)
    assert validated.specifications[0].status == "требует проверки"
