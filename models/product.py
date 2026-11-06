from typing import Literal

from pydantic import BaseModel, Field, field_validator


Status = Literal["подтверждено", "требует проверки", "данных нет"]


class SpecificationInput(BaseModel):
    name: str = Field(min_length=1)
    value: str | None = None
    unit: str | None = None
    source: str | None = None


class ProductInput(BaseModel):
    product_name: str | None = None
    manufacturer: str | None = None
    model: str | None = None
    short_description: str | None = None
    specifications: list[SpecificationInput] = Field(default_factory=list)
    source_text: str | None = None
    source_url: str | None = None

    def has_source_data(self) -> bool:
        return bool(any((self.product_name, self.manufacturer, self.model, self.short_description,
                         self.source_text, self.source_url, self.specifications)))


class SpecificationOutput(BaseModel):
    parameter: str = Field(min_length=1)
    value: str = "Данных нет"
    unit: str | None = None
    original_text: str | None = None
    source_reference: str | None = None
    status: Status = "данных нет"


class SalesBlock(BaseModel):
    target_audience: str = "Данных нет"
    tasks: str = "Данных нет"
    applications: str = "Данных нет"


class SourceReference(BaseModel):
    source_type: str
    source_name: str
    source_url: str | None = None
    extracted_at: str | None = None


class ProductCard(BaseModel):
    seo_title: str = "Данных нет"
    seo_description: str = "Данных нет"
    specifications: list[SpecificationOutput] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)
    sales_block: SalesBlock = Field(default_factory=SalesBlock)
    warnings: list[str] = Field(default_factory=list)
    sources: list[SourceReference] = Field(default_factory=list)

    @field_validator("seo_title")
    @classmethod
    def title_limit(cls, value: str) -> str:
        if len(value) > 70:
            raise ValueError("SEO-заголовок не должен превышать 70 символов")
        return value

    @field_validator("search_queries")
    @classmethod
    def query_count(cls, value: list[str]) -> list[str]:
        if value and not 3 <= len(value) <= 5:
            raise ValueError("Необходимо от 3 до 5 поисковых запросов")
        return value
