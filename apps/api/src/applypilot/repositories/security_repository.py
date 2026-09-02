from datetime import UTC, datetime

from sqlalchemy.orm import Session

from applypilot.models.security_event import SecurityEvent

ALLOWED_METADATA = {"reason", "revoked_count", "client_label"}


class SecurityRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def record(self, event_type: str, metadata: dict[str, str] | None = None) -> None:
        safe = {key: value for key, value in (metadata or {}).items() if key in ALLOWED_METADATA}
        self.database.add(
            SecurityEvent(event_type=event_type, created_at=datetime.now(UTC), metadata_json=safe)
        )
