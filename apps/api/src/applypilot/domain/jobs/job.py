from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class SourceJob:
    source_record_id: str
    title: str
    employer: str
    source_url: str
    application_url: str | None
    description_text: str
    original_location: str | None
    remote_classification: str | None
    employment_type: str | None
    published_at: datetime | None
    updated_at: datetime | None
    attribution: str
    raw: dict[str, Any] = field(repr=False)
