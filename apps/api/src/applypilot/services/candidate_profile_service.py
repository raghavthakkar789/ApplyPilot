from datetime import UTC, datetime

from sqlalchemy.orm import Session

from applypilot.models.candidate_profile import CandidateProfile
from applypilot.repositories.candidate_profile_repository import CandidateProfileRepository
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.schemas.profile import ProfileSections


class CandidateProfileService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.repository = CandidateProfileRepository(database)
        self.events = SecurityRepository(database)

    def get(self) -> CandidateProfile | None:
        return self.repository.get()

    def update(self, sections: ProfileSections, *, commit: bool = True) -> CandidateProfile:
        profile = self.get()
        now = datetime.now(UTC)
        if profile is not None:
            profile.sections = sections.model_dump(mode="json")
            profile.updated_at = now
            self.events.record("candidate_profile_updated")
            if commit:
                self.database.commit()
            return profile
        profile = CandidateProfile(
            owner_id=1,
            sections=sections.model_dump(mode="json"),
            created_at=now,
            updated_at=now,
        )
        self.database.add(profile)
        self.events.record("candidate_profile_created")
        if commit:
            self.database.commit()
        return profile
