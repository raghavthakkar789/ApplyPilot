from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class SessionIdentity:
    session_id: str
    owner_id: int
    absolute_expires_at: datetime
