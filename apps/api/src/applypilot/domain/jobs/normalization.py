import html
import re
from urllib.parse import urlsplit

TAG_PATTERN = re.compile(r"<[^>]*>")
SCRIPT_PATTERN = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.I | re.S)
SPACE_PATTERN = re.compile(r"\s+")


def safe_text(value: str) -> str:
    without_active = SCRIPT_PATTERN.sub(" ", value)
    return SPACE_PATTERN.sub(" ", html.unescape(TAG_PATTERN.sub(" ", without_active))).strip()


def safe_external_url(value: str | None) -> str | None:
    if not value:
        return None
    parsed = urlsplit(value.strip())
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Only safe HTTPS URLs are accepted.")
    return value.strip()


def normalized_key(employer: str, title: str, location: str | None) -> str:
    parts = (employer, title, location or "unknown")
    return "|".join(SPACE_PATTERN.sub(" ", part.casefold()).strip() for part in parts)
