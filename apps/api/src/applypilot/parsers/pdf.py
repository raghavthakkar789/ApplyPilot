from pathlib import Path

import pymupdf

from applypilot.domain.documents.document_limits import LIMITS
from applypilot.domain.documents.extraction_result import EvidenceSegment, ExtractionResult
from applypilot.parsers.base import DocumentParseError


class PdfParser:
    version = f"pymupdf-{pymupdf.__version__}"

    def parse(self, path: Path) -> ExtractionResult:
        try:
            document = pymupdf.open(path)  # type: ignore[no-untyped-call]
        except Exception as error:
            raise DocumentParseError("The PDF structure is invalid.") from error
        try:
            if document.needs_pass:
                raise DocumentParseError("Encrypted or password-protected PDFs are not supported.")
            if document.page_count > LIMITS.pdf_pages:
                raise DocumentParseError("The PDF exceeds the page safety limit.")
            segments: list[EvidenceSegment] = []
            warnings: list[str] = []
            total = 0
            for index in range(document.page_count):
                page = document[index]
                text = page.get_text("text").replace("\r\n", "\n").replace("\r", "\n")  # type: ignore[no-untyped-call]
                total += len(text)
                if total > LIMITS.extracted_characters:
                    raise DocumentParseError("The extracted text exceeds the safety limit.")
                if text.strip():
                    segments.append(EvidenceSegment(f"page {index + 1}", text))
                else:
                    warnings.append(
                        f"Page {index + 1} contains no extractable text; OCR was not run."
                    )
            return ExtractionResult(
                text="\n\n".join(segment.text for segment in segments),
                segments=tuple(segments),
                page_count=document.page_count,
                warnings=tuple(warnings),
            )
        finally:
            document.close()  # type: ignore[no-untyped-call]
