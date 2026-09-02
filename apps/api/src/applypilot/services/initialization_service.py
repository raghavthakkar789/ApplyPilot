from datetime import UTC, datetime, timedelta

from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from applypilot.core.security import PasswordPolicyError, hash_password, validate_password
from applypilot.models.installation import Installation
from applypilot.models.login_rate_limit import LoginRateLimit
from applypilot.models.owner_account import OwnerAccount
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.services.session_service import NewSession, SessionService


class InitializationUnavailable(Exception):
    pass


class InitializationThrottled(Exception):
    def __init__(self, retry_after: int) -> None:
        self.retry_after = retry_after


class InitializationService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.events = SecurityRepository(database)

    def is_required(self) -> bool:
        installation = self.database.get(Installation, 1)
        return installation is None or installation.initialized_at is None

    def initialize(self, password: str, confirmation: str, client_label: str | None) -> NewSession:
        now = datetime.now(UTC)
        try:
            self.database.execute(text("SELECT pg_advisory_xact_lock(4170706)"))
            installation = self.database.scalar(
                select(Installation).where(Installation.id == 1).with_for_update()
            )
            if installation is None:
                installation = Installation(id=1)
                self.database.add(installation)
                self.database.flush()
            if installation.initialized_at is not None:
                raise InitializationUnavailable
            limiter = self.database.get(LoginRateLimit, "initialization")
            if limiter is None:
                limiter = LoginRateLimit(
                    rate_key="initialization",
                    consecutive_failures=0,
                    window_started_at=now,
                    window_attempts=0,
                    updated_at=now,
                )
                self.database.add(limiter)
            if limiter.window_started_at is None or now - limiter.window_started_at >= timedelta(
                minutes=5
            ):
                limiter.window_started_at = now
                limiter.window_attempts = 0
            if limiter.window_attempts >= 3:
                remaining = 300 - int((now - limiter.window_started_at).total_seconds())
                self.events.record("initialization_failure", {"reason": "throttled"})
                self.database.commit()
                raise InitializationThrottled(max(1, remaining))
            limiter.window_attempts += 1
            if password != confirmation:
                raise ValueError("Passwords do not match.")
            validate_password(password)
            owner = OwnerAccount(
                id=1,
                password_verifier=hash_password(password),
                credential_version=1,
                created_at=now,
                password_changed_at=now,
            )
            self.database.add(owner)
            installation.initialized_at = now
            self.events.record("initialization_success")
            new_session = SessionService(self.database).create(owner, client_label)
            self.database.commit()
            return new_session
        except (InitializationUnavailable, InitializationThrottled):
            self.database.rollback()
            raise
        except (PasswordPolicyError, ValueError):
            self.events.record("initialization_failure")
            self.database.commit()
            raise
        except IntegrityError:
            self.database.rollback()
            raise
