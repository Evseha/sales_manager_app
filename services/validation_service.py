from models.product import ProductCard, ProductInput, SpecificationOutput


def _source_values(product: ProductInput) -> set[tuple[str, str, str | None]]:
    return {(item.name.casefold(), item.value or "Данных нет", item.unit) for item in product.specifications}


def validate_card(card: ProductCard, product: ProductInput, source_text: str | None = None) -> ProductCard:
    """Keep a value only when its parameter and value occur in a supplied source."""
    warnings = list(dict.fromkeys(card.warnings))
    allowed = _source_values(product)
    conflicting_values: dict[str, set[str]] = {}
    for item in product.specifications:
        if item.value:
            conflicting_values.setdefault(item.name.casefold(), set()).add(item.value)
    validated_specs: list[SpecificationOutput] = []
    for specification in card.specifications:
        key = (specification.parameter.casefold(), specification.value, specification.unit)
        in_text_source = bool(source_text and specification.parameter.casefold() in source_text.casefold()
                              and specification.value.casefold() in source_text.casefold())
        if specification.value != "Данных нет" and key not in allowed and not in_text_source:
            warnings.append(f"Характеристика «{specification.parameter}» не подтверждена источником и исключена.")
            continue
        if len(conflicting_values.get(specification.parameter.casefold(), set())) > 1:
            warnings.append(f"Для параметра «{specification.parameter}» есть противоречивые значения; требуется проверка.")
            specification = specification.model_copy(update={"status": "требует проверки"})
        validated_specs.append(specification)
    if len(card.seo_title) > 70:
        warnings.append("SEO-заголовок длиннее 70 символов и требует редактирования.")
    if card.seo_description != "Данных нет" and not 800 <= len(card.seo_description) <= 1200:
        warnings.append("SEO-описание короче или длиннее целевого диапазона; оно не дополнялось предположениями.")
    if not 3 <= len(card.search_queries) <= 5:
        warnings.append("Количество поисковых запросов должно быть от 3 до 5.")
    return card.model_copy(update={"specifications": validated_specs, "warnings": warnings})
