from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from applypilot.core.security import hash_password, validate_password
from applypilot.models.owner_account import OwnerAccount
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.repositories.session_repository import SessionRepository


class PasswordRecoveryService:
    def __init__(self, database: Session) -> None:
        self.database = database

    def reset(self, password: str, confirmation: str) -> None:
        if password != confirmation:
            raise ValueError("Passwords do not match.")
        validate_password(password)
        now = datetime.now(UTC)
        with self.database.begin():
            owner = self.database.scalar(select(OwnerAccount).with_for_update())
            if owner is None:
                raise ValueError("Recovery could not be completed.")
            owner.password_verifier = hash_password(password)
            owner.credential_version += 1
            owner.password_changed_at = now
            SessionRepository(self.database).revoke_all(now, "password_recovery")
            SecurityRepository(self.database).record("password_recovery")
