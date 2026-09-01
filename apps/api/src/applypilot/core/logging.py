import logging
from collections.abc import Mapping
from typing import Any

REDACTED_KEYS = {"authorization", "cookie", "password", "secret", "session", "token"}


class RedactionFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.args, Mapping):
            record.args = {
                key: "[REDACTED]" if str(key).lower() in REDACTED_KEYS else value
                for key, value in record.args.items()
            }
        return True


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler()
    handler.addFilter(RedactionFilter())
    logging.basicConfig(level=level.upper(), handlers=[handler], force=True)


def safe_log_context(values: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: "[REDACTED]" if key.lower() in REDACTED_KEYS else value
        for key, value in values.items()
    }
