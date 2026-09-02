from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from applypilot.core.security import DUMMY_PASSWORD_VERIFIER, verify_password
from applypilot.core.throttling import login_delay_seconds
from applypilot.models.login_rate_limit import LoginRateLimit
from applypilot.models.owner_account import OwnerAccount
from applypilot.repositories.owner_repository import OwnerRepository
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.services.session_service import NewSession, SessionService


class AuthenticationFailed(Exception):
    pass


class LoginThrottled(Exception):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after


class AuthenticationService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.events = SecurityRepository(database)

    def login(self, password: str, client_label: str | None) -> NewSession:
        now = datetime.now(UTC)
        self.database.execute(text("SELECT pg_advisory_xact_lock(4170707)"))
        limiter = self.database.get(LoginRateLimit, "owner_login")
        if limiter is None:
            limiter = LoginRateLimit(
                rate_key="owner_login", consecutive_failures=0, window_attempts=0, updated_at=now
            )
            self.database.add(limiter)
            self.database.flush()
        if limiter.blocked_until is not None and now < limiter.blocked_until:
            retry_after = max(1, int((limiter.blocked_until - now).total_seconds()) + 1)
            self.events.record("throttled_login")
            self.database.commit()
            raise LoginThrottled(retry_after)
        owner = OwnerRepository(self.database).owner()
        verifier = owner.password_verifier if owner is not None else DUMMY_PASSWORD_VERIFIER
        valid = verify_password(verifier, password) and owner is not None
        if not valid:
            limiter.consecutive_failures += 1
            delay = login_delay_seconds(limiter.consecutive_failures)
            limiter.blocked_until = now + timedelta(seconds=delay) if delay else None
            limiter.updated_at = now
            self.events.record("failed_login")
            if delay:
                self.events.record("throttled_login")
            self.database.commit()
            if delay:
                raise LoginThrottled(delay)
            raise AuthenticationFailed
        assert isinstance(owner, OwnerAccount)
        limiter.consecutive_failures = 0
        limiter.blocked_until = None
        limiter.updated_at = now
        new_session = SessionService(self.database).create(owner, client_label)
        self.events.record("successful_login", {"client_label": client_label or "unknown"})
        self.database.commit()
        return new_session
