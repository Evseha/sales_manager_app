from dataclasses import dataclass
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup


@dataclass
class ExtractedSource:
    url: str
    title: str | None = None
    meta_description: str | None = None
    visible_text: str | None = None
    error: str | None = None
    extracted_at: str | None = None


def extract_product_page(url: str, timeout: int) -> ExtractedSource:
    if not url.startswith(("http://", "https://")):
        return ExtractedSource(url=url, error="URL должен начинаться с http:// или https://")
    try:
        response = requests.get(url, timeout=timeout, headers={"User-Agent": "AI-Product-Assistant/1.0"})
        response.raise_for_status()
    except requests.RequestException as exc:
        return ExtractedSource(url=url, error=f"Не удалось получить страницу: {exc}")
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    title = soup.title.get_text(" ", strip=True) if soup.title else None
    meta = soup.find("meta", attrs={"name": "description"})
    description = meta.get("content", "").strip() if meta else None
    text = " ".join(soup.get_text(" ", strip=True).split())
    return ExtractedSource(
        url=url, title=title, meta_description=description, visible_text=text or None,
        extracted_at=datetime.now(timezone.utc).isoformat(),
        error=None if text else "На странице не найден читаемый текст.",
    )
