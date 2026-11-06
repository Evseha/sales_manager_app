import re


def safe_filename(value: str | None, fallback: str = "product_card") -> str:
    cleaned = re.sub(r"[^\w.-]+", "_", value or "", flags=re.UNICODE).strip("._")
    return cleaned[:80] or fallback
