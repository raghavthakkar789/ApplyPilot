from pathlib import Path

from applypilot.domain.documents.document_limits import LIMITS
from applypilot.domain.documents.extraction_result import EvidenceSegment, ExtractionResult
from applypilot.parsers.base import DocumentParseError


class TextParser:
    version = "stdlib-utf8-1"

    def parse(self, path: Path) -> ExtractionResult:
        raw = path.read_bytes()
        if b"\x00" in raw:
            raise DocumentParseError("The text document contains binary data.")
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError as error:
            raise DocumentParseError("The text document is not valid UTF-8.") from error
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        if len(text) > LIMITS.extracted_characters:
            raise DocumentParseError("The extracted text exceeds the safety limit.")
        segments = tuple(
            EvidenceSegment(f"line {number}", line)
            for number, line in enumerate(text.splitlines(), 1)
            if line.strip()
        )
        return ExtractionResult(text=text, segments=segments, paragraph_count=len(segments))
