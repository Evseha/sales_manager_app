import json

import pandas as pd
import streamlit as st

from config.settings import get_settings
from models.product import ProductCard, ProductInput, SalesBlock, SpecificationInput, SpecificationOutput
from services.gemini_service import GeminiService, GeminiServiceError
from services.product_generator import empty_card, generate_card
from services.source_extractor import ExtractedSource, extract_product_page
from utils.export import card_to_json, card_to_markdown, card_to_text
from utils.text_utils import safe_filename


st.set_page_config(page_title="AI Product Assistant", layout="wide")
st.title("AI Product Assistant")
st.caption("Карточка создаётся только по предоставленным источникам. Отсутствующие сведения не дополняются предположениями.")


def load_uploaded_product(uploaded) -> dict:
    if not uploaded:
        return {}
    try:
        return json.loads(uploaded.getvalue().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        st.error("Файл должен быть корректным JSON в кодировке UTF-8.")
        return {}


with st.sidebar:
    st.header("Исходные данные")
    uploaded = st.file_uploader("JSON с исходными данными", type="json")
    uploaded_data = load_uploaded_product(uploaded)
    product_name = st.text_input("Название товара", value=uploaded_data.get("product_name", ""))
    manufacturer = st.text_input("Производитель", value=uploaded_data.get("manufacturer", ""))
    model = st.text_input("Модель", value=uploaded_data.get("model", ""))
    short_description = st.text_area("Краткое описание", value=uploaded_data.get("short_description", ""))
    source_url = st.text_input("URL страницы товара", value=uploaded_data.get("source_url", ""))
    source_text = st.text_area("Текст паспорта, руководства или каталога", value=uploaded_data.get("source_text", ""), height=180)
    raw_specs = uploaded_data.get("specifications", [])
    spec_frame = pd.DataFrame(raw_specs or [{"name": "", "value": "", "unit": "", "source": "ручной ввод"}])
    specs_table = st.data_editor(spec_frame, num_rows="dynamic", use_container_width=True,
                                 column_config={"name": "Параметр", "value": "Значение", "unit": "Ед.", "source": "Источник"})
    extract_clicked = st.button("Извлечь сведения из URL")
    generate_clicked = st.button("Сформировать товарную карточку", type="primary")


def current_product() -> ProductInput:
    specs = []
    for row in specs_table.fillna("").to_dict("records"):
        if str(row.get("name", "")).strip():
            specs.append(SpecificationInput(name=str(row["name"]), value=str(row.get("value") or "") or None,
                                            unit=str(row.get("unit") or "") or None,
                                            source=str(row.get("source") or "") or None))
    return ProductInput(product_name=product_name or None, manufacturer=manufacturer or None, model=model or None,
                        short_description=short_description or None, source_url=source_url or None,
                        source_text=source_text or None, specifications=specs)


if extract_clicked:
    if not source_url:
        st.warning("Укажите URL для извлечения.")
    else:
        with st.spinner("Получаю страницу..."):
            extracted = extract_product_page(source_url, get_settings().request_timeout)
        st.session_state["extracted"] = extracted

extracted: ExtractedSource | None = st.session_state.get("extracted")
if extracted:
    st.subheader("Извлечённые сведения")
    if extracted.error:
        st.warning(extracted.error)
    else:
        st.write({"Заголовок": extracted.title, "Мета-описание": extracted.meta_description, "Время": extracted.extracted_at})
        st.text_area("Видимый текст страницы", value=extracted.visible_text or "", height=220, disabled=True)

if generate_clicked:
    product = current_product()
    if not product.has_source_data():
        st.session_state["card"] = empty_card(product, "Добавьте хотя бы один содержательный источник данных.")
    else:
        try:
            with st.spinner("Формирую карточку..."):
                text = extracted.visible_text if extracted and not extracted.error else None
                st.session_state["card"] = generate_card(product, GeminiService(get_settings()), text)
        except GeminiServiceError as exc:
            st.error(str(exc))

card: ProductCard | None = st.session_state.get("card")
if card:
    st.subheader("Результат")
    title = st.text_input("SEO-заголовок", value=card.seo_title, max_chars=70)
    description = st.text_area("SEO-описание", value=card.seo_description, height=220)
    st.caption(f"Символов в описании: {len(description)}")
    spec_result = pd.DataFrame([item.model_dump() for item in card.specifications])
    edited_specs = st.data_editor(spec_result, num_rows="dynamic", use_container_width=True, key="result_specs")
    queries = st.text_area("Поисковые запросы: по одному на строку", value="\n".join(card.search_queries))
    audience = st.text_area("Кому подходит", value=card.sales_block.target_audience, key="audience")
    tasks = st.text_area("Задачи", value=card.sales_block.tasks, key="tasks")
    applications = st.text_area("Применение", value=card.sales_block.applications, key="applications")
    if card.warnings:
        st.subheader("Источники и предупреждения")
        for warning in card.warnings:
            st.warning(warning)
    for source in card.sources:
        st.write(f"{source.source_type}: {source.source_name} {source.source_url or ''}")
    try:
        output_specs = [SpecificationOutput.model_validate(row) for row in edited_specs.fillna("").to_dict("records")]
        edited_card = card.model_copy(update={
            "seo_title": title, "seo_description": description,
            "search_queries": [query.strip() for query in queries.splitlines() if query.strip()],
            "specifications": output_specs,
            "sales_block": SalesBlock(target_audience=audience, tasks=tasks, applications=applications),
        })
    except Exception:
        edited_card = card
        st.warning("Некоторые изменения не соответствуют формату карточки; экспортирована последняя корректная версия.")
    basename = safe_filename(model or product_name)
    columns = st.columns(3)
    columns[0].download_button("Скачать JSON", card_to_json(edited_card), f"{basename}.json", "application/json")
    columns[1].download_button("Скачать Markdown", card_to_markdown(edited_card), f"{basename}.md", "text/markdown")
    columns[2].download_button("Скачать TXT", card_to_text(edited_card), f"{basename}.txt", "text/plain")
