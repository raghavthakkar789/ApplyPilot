import hashlib
import signal
import threading
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from applypilot.domain.documents.document_limits import LIMITS
from applypilot.domain.documents.document_type import DocumentFormat
from applypilot.domain.documents.extraction_result import ExtractionResult
from applypilot.parsers import DocxParser, PdfParser, TextParser
from applypilot.parsers.base import DocumentParseError, DocumentParser


class DocumentExtractionService:
    def extract(self, path: Path, document_format: DocumentFormat) -> ExtractionResult:
        parser: DocumentParser
        if document_format == DocumentFormat.PDF:
            parser = PdfParser()
        elif document_format == DocumentFormat.DOCX:
            parser = DocxParser()
        else:
            parser = TextParser()
        started = time.monotonic()
        with parser_deadline(LIMITS.parsing_seconds):
            result = parser.parse(path)
        if time.monotonic() - started > LIMITS.parsing_seconds:
            raise DocumentParseError("Document parsing exceeded the safety timeout.")
        return result

    @staticmethod
    def integrity_hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()


@contextmanager
def parser_deadline(seconds: float) -> Iterator[None]:
    """Enforce a hard Linux deadline in the production main thread.

    TestClient runs the ASGI loop in a portal thread where POSIX alarms are not
    available; the elapsed-time guard above remains active there.
    """
    if threading.current_thread() is not threading.main_thread():
        yield
        return

    def timeout_handler(_signum: int, _frame: object) -> None:
        raise DocumentParseError("Document parsing exceeded the safety timeout.")

    previous = signal.signal(signal.SIGALRM, timeout_handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)
