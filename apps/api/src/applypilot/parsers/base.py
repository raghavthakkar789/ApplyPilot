from pathlib import Path
from typing import Protocol

from applypilot.domain.documents.extraction_result import ExtractionResult


class DocumentParser(Protocol):
    version: str

    def parse(self, path: Path) -> ExtractionResult: ...


class DocumentParseError(ValueError):
    """A safe parser failure suitable for translating into a client error."""
