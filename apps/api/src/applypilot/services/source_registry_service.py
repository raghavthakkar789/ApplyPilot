from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from applypilot.adapters.jobs import ADAPTERS
from applypilot.models.job import AtsRegistryEntry
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.repositories.source_registry_repository import SourceRegistryRepository
from applypilot.schemas.job import RegistryInput


class SourceRegistryService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.repository = SourceRegistryRepository(database)
        self.events = SecurityRepository(database)

    async def create_and_validate(self, value: RegistryInput) -> AtsRegistryEntry:
        now = datetime.now(UTC)
        entry = AtsRegistryEntry(
            provider=value.provider,
            employer_name=value.employer_name.strip(),
            employer_domain=value.employer_domain.casefold(),
            board_identifier=value.board_identifier,
            careers_url=str(value.careers_url),
            state="validating",
            verification_method=value.verification_method,
            enabled=False,
            created_at=now,
            updated_at=now,
        )
        self.database.add(entry)
        self.database.flush()
        try:
            jobs = await ADAPTERS[value.provider].retrieve(
                value.board_identifier, value.employer_name
            )
            if not jobs:
                raise ValueError("empty_board")
            if not all(value.employer_name.casefold() == job.employer.casefold() for job in jobs):
                raise ValueError("employer_mismatch")
            entry.state = "validated"
            entry.verified_at = now
            entry.last_success_at = now
            entry.enabled = True
            self.events.record(
                "source_registry_validated",
                {"registry_entry_id": entry.id, "provider": entry.provider},
            )
        except Exception as error:
            entry.state = "invalid"
            entry.last_failure_category = self._failure_category(error)
            entry.enabled = False
        self.events.record(
            "source_registry_created", {"registry_entry_id": entry.id, "provider": entry.provider}
        )
        self.database.commit()
        return entry

    @staticmethod
    def _failure_category(error: Exception) -> str:
        if isinstance(error, ValueError) and str(error) in {
            "empty_board",
            "employer_mismatch",
        }:
            return str(error)
        return "provider_validation_failed"

    def set_enabled(self, entry_id: str, enabled: bool) -> AtsRegistryEntry:
        entry = self.repository.entry(entry_id, lock=True)
        if entry is None:
            raise HTTPException(404, "Registry entry not found.")
        if enabled and entry.state != "validated":
            raise HTTPException(409, "Validate this entry before enabling it.")
        entry.enabled = enabled
        entry.updated_at = datetime.now(UTC)
        self.events.record(
            "source_registry_enabled" if enabled else "source_registry_disabled",
            {"registry_entry_id": entry.id},
        )
        self.database.commit()
        return entry
