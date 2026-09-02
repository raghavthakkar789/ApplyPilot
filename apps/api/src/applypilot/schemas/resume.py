from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ExtractionSegmentResponse(BaseModel):
    citation: str
    text: str


class ExtractionResponse(BaseModel):
    status: Literal["pending", "succeeded", "failed"]
    text: str | None = None
    page_count: int | None = None
    paragraph_count: int | None = None
    segments: list[ExtractionSegmentResponse] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    extracted_at: datetime | None = None
    failure_category: str | None = None


class ResumeVersionResponse(BaseModel):
    id: str
    version_number: int
    filename: str
    media_type: str
    format: Literal["pdf", "docx", "text"]
    byte_length: int
    sha256: str
    parser: str
    parser_version: str
    extraction_status: Literal["pending", "succeeded", "failed"]
    integrity_state: str
    created_at: datetime
    superseded_at: datetime | None
    current: bool


class ResumeResponse(BaseModel):
    id: str
    display_name: str
    purpose: str | None
    created_at: datetime
    trashed_at: datetime | None
    purge_after: datetime | None
    current_version: ResumeVersionResponse | None


class ResumeListResponse(BaseModel):
    resumes: list[ResumeResponse]


class ResumeDetailResponse(ResumeResponse):
    versions: list[ResumeVersionResponse]


class ResumeMutationResponse(BaseModel):
    id: str
    status: str
