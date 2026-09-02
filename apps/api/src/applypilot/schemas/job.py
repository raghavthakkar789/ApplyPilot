from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ManualJobInput(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    employer: str = Field(min_length=1, max_length=160)
    location: str | None = Field(default=None, max_length=255)
    work_mode: str | None = Field(default=None, max_length=40)
    employment_type: str | None = Field(default=None, max_length=80)
    description: str = Field(default="", max_length=200_000)
    source_url: HttpUrl | None = None
    application_url: HttpUrl | None = None
    compensation: str | None = Field(default=None, max_length=500)
    publication_date: datetime | None = None
    closing_date: datetime | None = None
    notes: str | None = Field(default=None, max_length=10_000)


class JobSourceResponse(BaseModel):
    provider: str
    source_url: str
    application_url: str | None
    attribution: str
    retrieved_at: datetime


class JobResponse(BaseModel):
    id: str
    title: str
    employer: str
    description: str
    location: str | None
    work_mode: str | None
    employment_type: str | None
    freshness_state: str
    saved: bool
    version_number: int
    created_at: datetime
    sources: list[JobSourceResponse]
    match_status: Literal["not_evaluated"] = "not_evaluated"


class JobListResponse(BaseModel):
    jobs: list[JobResponse]
    partial_failures: list[str] = Field(default_factory=list)


class JobVersionResponse(BaseModel):
    id: str
    version_number: int
    title: str
    employer: str
    freshness_state: str
    normalization_warnings: list[object]
    created_at: datetime


class RegistryInput(BaseModel):
    provider: Literal["greenhouse", "lever", "ashby"]
    employer_name: str = Field(min_length=1, max_length=160)
    employer_domain: str = Field(pattern=r"^[A-Za-z0-9.-]+\.[A-Za-z]{2,}$", max_length=253)
    board_identifier: str = Field(pattern=r"^[A-Za-z0-9-]+$", max_length=160)
    careers_url: HttpUrl
    verification_method: str = Field(min_length=3, max_length=80)


class RegistryResponse(BaseModel):
    id: str
    provider: str
    employer_name: str
    employer_domain: str
    board_identifier: str
    careers_url: str
    state: str
    enabled: bool
    verified_at: datetime | None
    last_success_at: datetime | None
    last_failure_category: str | None


class SyncResponse(BaseModel):
    id: str
    provider: str
    status: str
    records_seen: int
    records_changed: int
    safe_failure_category: str | None
    started_at: datetime
    finished_at: datetime | None


class DeduplicationResolution(BaseModel):
    reason: str = Field(min_length=3, max_length=500)


class DeduplicationCandidateResponse(BaseModel):
    id: str
    left_job_id: str
    right_job_id: str
    reasons: list[object]
    status: str
    owner_reason: str | None
    created_at: datetime
    resolved_at: datetime | None
