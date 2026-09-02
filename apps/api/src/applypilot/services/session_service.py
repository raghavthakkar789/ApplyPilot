from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from applypilot.core.security import generate_token, hash_token
from applypilot.models.csrf_token import SessionCsrfToken
from applypilot.models.owner_account import OwnerAccount
from applypilot.models.session import OwnerSession
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.repositories.session_repository import SessionRepository

IDLE_TIMEOUT = timedelta(minutes=60)
ABSOLUTE_TIMEOUT = timedelta(hours=12)
ACTIVITY_WRITE_INTERVAL = timedelta(minutes=5)
MAX_ACTIVE_SESSIONS = 3


@dataclass(frozen=True)
class NewSession:
    session: OwnerSession
    raw_session_token: str
    raw_csrf_token: str


class SessionService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.repository = SessionRepository(database)
        self.events = SecurityRepository(database)

    def create(self, owner: OwnerAccount, client_label: str | None) -> NewSession:
        now = datetime.now(UTC)
        self.database.execute(text("SELECT pg_advisory_xact_lock(4170708)"))
        raw_session = generate_token()
        raw_csrf = generate_token()
        session = OwnerSession(
            owner_id=owner.id,
            token_hash=hash_token(raw_session),
            created_at=now,
            last_activity_at=now,
            idle_expires_at=now + IDLE_TIMEOUT,
            absolute_expires_at=now + ABSOLUTE_TIMEOUT,
            credential_version=owner.credential_version,
            client_label=client_label,
        )
        session.csrf_token = SessionCsrfToken(
            token_hash=hash_token(raw_csrf), created_at=now, expires_at=now + ABSOLUTE_TIMEOUT
        )
        self.database.add(session)
        self.database.flush()
        active = self.repository.active(now)
        for old_session in active[MAX_ACTIVE_SESSIONS:]:
            old_session.revoked_at = now
            old_session.revocation_reason = "session_limit"
            self.events.record("individual_revocation", {"reason": "session_limit"})
        return NewSession(session, raw_session, raw_csrf)

    def authenticate(
        self, raw_token: str, owner: OwnerAccount
    ) -> tuple[OwnerSession | None, str | None]:
        now = datetime.now(UTC)
        session = self.repository.by_token_hash(hash_token(raw_token))
        if session is None or session.revoked_at is not None:
            return None, None
        if session.credential_version != owner.credential_version:
            session.revoked_at = now
            session.revocation_reason = "credential_version"
            self.events.record("credential_version_invalidation")
            self.database.commit()
            return None, None
        expiry_type = None
        if now >= session.absolute_expires_at:
            expiry_type = "absolute_expiry"
        elif now >= session.idle_expires_at:
            expiry_type = "idle_expiry"
        if expiry_type:
            session.revoked_at = now
            session.revocation_reason = expiry_type
            self.events.record(expiry_type)
            self.database.commit()
            return None, None
        if now - session.last_activity_at >= ACTIVITY_WRITE_INTERVAL:
            session.last_activity_at = now
            session.idle_expires_at = min(now + IDLE_TIMEOUT, session.absolute_expires_at)
            self.database.commit()
        return session, raw_token

    def revoke(self, session: OwnerSession, reason: str, event_type: str) -> None:
        if session.revoked_at is None:
            session.revoked_at = datetime.now(UTC)
            session.revocation_reason = reason
            self.events.record(event_type, {"reason": reason})

    def revoke_others(self, current: OwnerSession) -> int:
        now = datetime.now(UTC)
        count = 0
        for session in self.repository.active(now):
            if session.id != current.id:
                session.revoked_at = now
                session.revocation_reason = "owner_revoke_others"
                count += 1
        self.events.record("all_other_session_revocation", {"revoked_count": str(count)})
        return count
