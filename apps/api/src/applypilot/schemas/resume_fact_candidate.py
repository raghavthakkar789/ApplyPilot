from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ResumeFactCandidateResponse(BaseModel):
    id: str
    resume_version_id: str
    fact_type: str
    semantic_key: str
    proposed_value: object
    evidence_citation: str
    extraction_method: str
    confidence: str | None
    review_status: Literal["pending", "accepted", "rejected"]
    created_at: datetime
    reviewed_at: datetime | None
    resulting_fact_identity_id: str | None
    resulting_fact_version_id: str | None


class ResumeFactCandidateListResponse(BaseModel):
    candidates: list[ResumeFactCandidateResponse]


class CandidateAcceptanceResponse(BaseModel):
    candidate_id: str
    fact_identity_id: str
    fact_version_id: str
    fact_state: Literal["unverified"] = "unverified"
