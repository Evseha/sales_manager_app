from models.product import ProductCard, ProductInput, SalesBlock, SourceReference
from services.gemini_service import GeminiService
from services.validation_service import validate_card


def source_references(product: ProductInput) -> list[SourceReference]:
    sources: list[SourceReference] = []
    if product.source_text:
        sources.append(SourceReference(source_type="ручной текст", source_name="Вставленный пользователем текст"))
    if product.source_url:
        sources.append(SourceReference(source_type="URL", source_name="Страница товара", source_url=product.source_url))
    if product.specifications:
        sources.append(SourceReference(source_type="ручной ввод", source_name="Список характеристик"))
    return sources


def empty_card(product: ProductInput, warning: str) -> ProductCard:
    specs = [
        {"parameter": item.name, "value": item.value or "Данных нет", "unit": item.unit,
         "original_text": item.value, "source_reference": item.source or "ручной ввод",
         "status": "подтверждено" if item.value else "данных нет"}
        for item in product.specifications
    ]
    return ProductCard(specifications=specs, sales_block=SalesBlock(), warnings=[warning], sources=source_references(product))


def generate_card(product: ProductInput, service: GeminiService, extracted_text: str | None = None) -> ProductCard:
    if not product.has_source_data():
        return empty_card(product, "Добавьте хотя бы один источник данных перед генерацией.")
    card = service.generate(product, extracted_text)
    card = card.model_copy(update={"sources": card.sources or source_references(product)})
    all_text = "\n".join(filter(None, [product.source_text, extracted_text]))
    return validate_card(card, product, all_text)
