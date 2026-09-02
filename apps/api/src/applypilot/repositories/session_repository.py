from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from applypilot.models.csrf_token import SessionCsrfToken
from applypilot.models.session import OwnerSession


class SessionRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def by_token_hash(self, token_hash: str) -> OwnerSession | None:
        return self.database.scalar(
            select(OwnerSession).where(OwnerSession.token_hash == token_hash)
        )

    def active(self, now: datetime) -> list[OwnerSession]:
        return list(
            self.database.scalars(
                select(OwnerSession)
                .where(
                    OwnerSession.revoked_at.is_(None),
                    OwnerSession.idle_expires_at > now,
                    OwnerSession.absolute_expires_at > now,
                )
                .order_by(OwnerSession.last_activity_at.desc())
            )
        )

    def get(self, session_id: str) -> OwnerSession | None:
        return self.database.get(OwnerSession, session_id)

    def csrf(self, session_id: str) -> SessionCsrfToken | None:
        return self.database.get(SessionCsrfToken, session_id)

    def revoke_all(self, now: datetime, reason: str) -> int:
        result = self.database.execute(
            update(OwnerSession)
            .where(OwnerSession.revoked_at.is_(None))
            .values(revoked_at=now, revocation_reason=reason)
        )
        return int(result.rowcount or 0)
