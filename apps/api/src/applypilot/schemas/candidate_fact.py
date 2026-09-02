from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

FactStateValue = Literal["unverified", "verified", "stale", "conflicted", "revoked"]


class FactCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    fact_type: str = Field(min_length=1, max_length=64)
    semantic_key: str = Field(min_length=1, max_length=160)
    scope: str = Field(default="*", min_length=1, max_length=160)
    value: object
    source_type: str = Field(default="owner_entry", min_length=1, max_length=32)
    source_reference: str | None = Field(default=None, max_length=240)
    source_version: str | None = Field(default=None, max_length=120)
    evidence_citation: str | None = Field(default=None, max_length=500)
    extraction_method: str | None = Field(default=None, max_length=80)
    extraction_confidence: Literal["high", "medium", "low"] | None = None
    sensitivity: Literal["standard", "private", "eligibility", "highly_sensitive"] = "standard"
    reconfirmation_policy: Literal[
        "stable", "days_90", "days_30", "per_application", "per_destination_attempt"
    ] = "stable"


class FactEditRequest(FactCreateRequest):
    reason: str = Field(min_length=1, max_length=240)


class FactReasonRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=240)


class FactVersionResponse(BaseModel):
    id: str
    version_number: int
    value: object | None
    lifecycle_state: FactStateValue
    source_type: str
    source_reference: str | None
    source_version: str | None
    evidence_citation: str | None
    created_at: datetime
    owner_confirmed_at: datetime | None
    reconfirmation_policy: str
    confirmation_due_at: datetime | None
    sensitivity: str
    current: bool


class FactSummaryResponse(BaseModel):
    identity_id: str
    fact_type: str
    semantic_key: str
    scope: str
    current_version: FactVersionResponse


class FactDetailResponse(FactSummaryResponse):
    versions: list[FactVersionResponse]


class FactListResponse(BaseModel):
    facts: list[FactSummaryResponse]
