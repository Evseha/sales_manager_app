import pytest
from pydantic import ValidationError

from models.product import ProductCard, ProductInput, SpecificationInput


def test_product_input_detects_source_data():
    assert not ProductInput().has_source_data()
    assert ProductInput(specifications=[SpecificationInput(name="Напряжение", value="24")]).has_source_data()


def test_title_limit_is_enforced():
    with pytest.raises(ValidationError):
        ProductCard(seo_title="x" * 71)


def test_query_count_is_enforced_when_queries_exist():
    with pytest.raises(ValidationError):
        ProductCard(search_queries=["one", "two"])
