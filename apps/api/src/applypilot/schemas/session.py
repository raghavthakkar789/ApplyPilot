from datetime import datetime

from pydantic import BaseModel


class SessionResponse(BaseModel):
    id: str
    created_at: datetime
    last_activity_at: datetime
    idle_expires_at: datetime
    absolute_expires_at: datetime
    client_label: str | None
    current: bool


class SessionListResponse(BaseModel):
    sessions: list[SessionResponse]


class RevocationResponse(BaseModel):
    revoked_count: int


class CsrfResponse(BaseModel):
    csrf_token: str
