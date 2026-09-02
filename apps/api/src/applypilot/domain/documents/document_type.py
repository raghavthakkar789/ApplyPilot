from enum import StrEnum


class DocumentFormat(StrEnum):
    PDF = "pdf"
    DOCX = "docx"
    TEXT = "text"


MEDIA_TYPES = {
    DocumentFormat.PDF: "application/pdf",
    DocumentFormat.DOCX: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    DocumentFormat.TEXT: "text/plain",
}

EXTENSIONS = {DocumentFormat.PDF: ".pdf", DocumentFormat.DOCX: ".docx", DocumentFormat.TEXT: ".txt"}
