from dataclasses import dataclass
from pathlib import Path, PurePath

from applypilot.domain.documents.document_type import EXTENSIONS, MEDIA_TYPES, DocumentFormat
from applypilot.parsers.base import DocumentParseError, DocumentParser
from applypilot.parsers.docx import DocxParser
from applypilot.parsers.pdf import PdfParser
from applypilot.parsers.text import TextParser


@dataclass(frozen=True)
class ValidatedDocument:
    display_filename: str
    document_format: DocumentFormat
    media_type: str
    parser_name: str
    parser_version: str


class DocumentValidationService:
    def validate(
        self, path: Path, filename: str | None, declared_type: str | None
    ) -> ValidatedDocument:
        if not filename:
            raise DocumentParseError("A filename is required.")
        display = PurePath(filename.replace("\\", "/")).name.strip()
        if not display or len(display) > 255:
            raise DocumentParseError("The filename is invalid.")
        extension = Path(display).suffix.lower()
        formats = [kind for kind, suffix in EXTENSIONS.items() if suffix == extension]
        if not formats:
            raise DocumentParseError("Only PDF, DOCX, and UTF-8 TXT files are supported.")
        kind = formats[0]
        expected_type = MEDIA_TYPES[kind]
        if declared_type != expected_type:
            raise DocumentParseError("The filename and declared media type do not agree.")
        prefix = path.read_bytes()[:8]
        if kind == DocumentFormat.PDF and not prefix.startswith(b"%PDF-"):
            raise DocumentParseError("The PDF signature does not match its filename.")
        if kind == DocumentFormat.DOCX and not prefix.startswith(b"PK\x03\x04"):
            raise DocumentParseError("The DOCX signature does not match its filename.")
        if kind == DocumentFormat.TEXT and (
            prefix.startswith(b"%PDF-") or prefix.startswith(b"PK")
        ):
            raise DocumentParseError("The text file signature is ambiguous.")
        parser: DocumentParser
        if kind == DocumentFormat.PDF:
            parser = PdfParser()
        elif kind == DocumentFormat.DOCX:
            parser = DocxParser()
        else:
            parser = TextParser()
        return ValidatedDocument(
            display, kind, expected_type, parser.__class__.__name__, parser.version
        )
