import json

from models.product import ProductCard


def card_to_json(card: ProductCard) -> str:
    return json.dumps(card.model_dump(mode="json"), ensure_ascii=False, indent=2)


def card_to_markdown(card: ProductCard) -> str:
    lines = [f"# {card.seo_title}", "", card.seo_description, "", "## Характеристики", "",
             "| Параметр | Значение | Ед. | Статус | Источник |", "|---|---|---|---|---|"]
    for item in card.specifications:
        lines.append(f"| {item.parameter} | {item.value} | {item.unit or ''} | {item.status} | {item.source_reference or ''} |")
    lines += ["", "## Поисковые запросы", *[f"- {query}" for query in card.search_queries], "", "## Коммерческий блок",
              f"- Кому подходит: {card.sales_block.target_audience}", f"- Задачи: {card.sales_block.tasks}",
              f"- Применение: {card.sales_block.applications}"]
    if card.warnings:
        lines += ["", "## Предупреждения", *[f"- {warning}" for warning in card.warnings]]
    return "\n".join(lines)


def card_to_text(card: ProductCard) -> str:
    return card_to_markdown(card).replace("# ", "").replace("## ", "").replace("|", " ")
