from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentLimits:
    upload_bytes: int = 10 * 1024 * 1024
    pdf_pages: int = 250
    extracted_characters: int = 2_000_000
    docx_uncompressed_bytes: int = 50 * 1024 * 1024
    docx_entries: int = 2_000
    docx_compression_ratio: float = 100.0
    parsing_seconds: float = 15.0


LIMITS = DocumentLimits()
