from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from applypilot.models.resume import ResumeFactCandidate
from applypilot.repositories.candidate_fact_repository import CandidateFactRepository
from applypilot.repositories.resume_repository import ResumeRepository
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.schemas.candidate_fact import FactCreateRequest, FactEditRequest
from applypilot.services.candidate_fact_service import CandidateFactService


class ResumeCandidateService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.repository = ResumeRepository(database)
        self.events = SecurityRepository(database)

    def accept(self, candidate_id: str) -> tuple[str, str]:
        candidate = self._pending(candidate_id)
        version = self.repository.version(candidate.resume_version_id)
        if version is None:
            raise HTTPException(404, "Resume version not found.")
        common = dict(
            fact_type=candidate.fact_type,
            semantic_key=candidate.semantic_key,
            scope="*",
            value=candidate.proposed_value,
            source_type="resume",
            source_reference=version.resume_id,
            source_version=version.id,
            evidence_citation=candidate.evidence_citation,
            extraction_method=candidate.extraction_method,
            extraction_confidence=candidate.confidence,
            sensitivity="standard",
            reconfirmation_policy="stable",
        )
        existing = next(
            (
                item
                for item in CandidateFactRepository(self.database).identities()
                if item.semantic_key == candidate.semantic_key and item.scope == "*"
            ),
            None,
        )
        if existing is None:
            identity, fact = CandidateFactService(self.database).create(
                FactCreateRequest(**common), commit=False
            )
        else:
            identity, fact = CandidateFactService(self.database).edit(
                existing.id,
                FactEditRequest(**common, reason="Accepted resume extraction candidate"),
                commit=False,
            )
        candidate.review_status = "accepted"
        candidate.reviewed_at = datetime.now(UTC)
        candidate.resulting_fact_identity_id = identity.id
        candidate.resulting_fact_version_id = fact.id
        self.events.record("resume_candidate_accepted", {"candidate_id": candidate.id})
        self.database.commit()
        return identity.id, fact.id

    def reject(self, candidate_id: str) -> None:
        candidate = self._pending(candidate_id)
        candidate.review_status = "rejected"
        candidate.reviewed_at = datetime.now(UTC)
        self.events.record("resume_candidate_rejected", {"candidate_id": candidate.id})
        self.database.commit()

    def _pending(self, candidate_id: str) -> ResumeFactCandidate:
        candidate = self.repository.candidate(candidate_id, lock=True)
        if candidate is None:
            raise HTTPException(404, "Fact candidate not found.")
        if candidate.review_status != "pending":
            raise HTTPException(409, "This candidate has already been reviewed.")
        return candidate
