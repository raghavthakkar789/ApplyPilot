import re

from sqlalchemy.orm import Session

from applypilot.models.candidate_fact import CandidateFactVersion
from applypilot.repositories.owner_repository import OwnerRepository
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.schemas.candidate_fact import FactCreateRequest
from applypilot.schemas.profile import ProfileSections
from applypilot.services.candidate_fact_service import CandidateFactService
from applypilot.services.candidate_profile_service import CandidateProfileService

NAME_MAX_LENGTH = 160
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,24}$")
CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")


class OwnerDetailsImportError(ValueError):
    pass


def normalize_name(value: str) -> str:
    name = " ".join(value.split())
    if not name or len(name) > NAME_MAX_LENGTH or CONTROL_CHARACTERS.search(name) or "@" in name:
        raise OwnerDetailsImportError("Owner details import could not be completed.")
    return name


def normalize_email(value: str) -> str:
    email = value.strip().casefold()
    if not EMAIL_PATTERN.fullmatch(email) or ".." in email:
        raise OwnerDetailsImportError("Owner details import could not be completed.")
    return email


def mask_name(value: str) -> str:
    if len(value) <= 2:
        return "*" * len(value)
    return f"{value[0]}***{value[-1]}"


def mask_email(value: str) -> str:
    local, _, domain = value.partition("@")
    host, _, suffix = domain.partition(".")
    local_mask = f"{local[:1]}***" if local else "***"
    host_mask = f"{host[:1]}***" if host else "***"
    return f"{local_mask}@{host_mask}{'.' + suffix if suffix else ''}"


class OwnerDetailsImportService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.events = SecurityRepository(database)

    def import_details(self, name: str, email: str) -> dict[str, str]:
        if OwnerRepository(self.database).owner() is None:
            raise OwnerDetailsImportError("Owner details import requires an initialized owner.")
        normalized_name = normalize_name(name)
        normalized_email = normalize_email(email)
        profile_service = CandidateProfileService(self.database)
        existing = profile_service.get()
        sections = (
            ProfileSections.model_validate(existing.sections)
            if existing is not None
            else ProfileSections()
        )
        sections.identity = {**sections.identity, "preferred_name": normalized_name}
        sections.contact = {**sections.contact, "email": normalized_email}
        profile_service.update(sections, commit=False)
        facts = CandidateFactService(self.database)
        _, name_version, name_created = facts.upsert_unverified(
            FactCreateRequest(
                fact_type="identity",
                semantic_key="identity.preferred_name",
                value=normalized_name,
                source_type="local_shell_import",
                sensitivity="private",
                reconfirmation_policy="days_90",
            ),
            reason="local_shell_import",
            commit=False,
        )
        _, email_version, email_created = facts.upsert_unverified(
            FactCreateRequest(
                fact_type="contact",
                semantic_key="contact.email",
                value=normalized_email,
                source_type="local_shell_import",
                sensitivity="private",
                reconfirmation_policy="days_90",
            ),
            reason="local_shell_import",
            commit=False,
        )
        self._reject_automatic_verification(name_version, name_created)
        self._reject_automatic_verification(email_version, email_created)
        self.events.record("owner_details_imported", {"reason": "local_shell_import"})
        self.database.commit()
        return {
            "name": mask_name(normalized_name),
            "email": mask_email(normalized_email),
        }

    def _reject_automatic_verification(
        self, version: CandidateFactVersion, created: bool
    ) -> None:
        if created and version.lifecycle_state not in {"unverified", "conflicted"}:
            raise OwnerDetailsImportError("Owner details import could not be completed.")
        if created and version.owner_confirmed_at is not None:
            raise OwnerDetailsImportError("Owner details import could not be completed.")
