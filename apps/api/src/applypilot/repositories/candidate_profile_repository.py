from sqlalchemy.orm import Session

from applypilot.models.candidate_profile import CandidateProfile


class CandidateProfileRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def get(self) -> CandidateProfile | None:
        return self.database.get(CandidateProfile, 1)
