from datetime import datetime

from pydantic import BaseModel, Field

from applypilot.schemas.candidate_fact import FactVersionResponse


class ConflictSummaryResponse(BaseModel):
    id: str
    semantic_key: str
    status: str
    detected_at: datetime


class ConflictDetailResponse(ConflictSummaryResponse):
    members: list[FactVersionResponse]


class ConflictListResponse(BaseModel):
    conflicts: list[ConflictSummaryResponse]


class ConflictResolutionRequest(BaseModel):
    selected_version_id: str
    reason: str = Field(min_length=1, max_length=240)
