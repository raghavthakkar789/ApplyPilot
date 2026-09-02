from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from applypilot.domain.candidate_fact import FactState
from applypilot.domain.reconfirmation import confirmation_due_at
from applypilot.models.candidate_fact import CandidateFactConfirmation, CandidateFactLifecycleEvent
from applypilot.repositories.candidate_fact_repository import CandidateFactRepository
from applypilot.repositories.security_repository import SecurityRepository


class CandidateConflictService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.repository = CandidateFactRepository(database)
        self.events = SecurityRepository(database)

    def resolve(self, conflict_id: str, selected_version_id: str, reason: str) -> None:
        conflict = self.repository.conflict(conflict_id)
        if conflict is None or conflict.status != "open":
            raise HTTPException(404, "Open conflict not found.")
        members = self.repository.conflict_members(conflict_id)
        selected = next((member for member in members if member.id == selected_version_id), None)
        if selected is None:
            raise HTTPException(422, "Selected version is not part of this conflict.")
        if selected.reconfirmation_policy in {"per_application", "per_destination_attempt"}:
            raise HTTPException(409, "This fact requires an exact future application context.")
        now = datetime.now(UTC)
        for member in members:
            if member.id == selected.id:
                member.lifecycle_state = FactState.VERIFIED
                member.owner_confirmed_at = now
                member.reconfirmation_due_at = confirmation_due_at(
                    member.reconfirmation_policy, now
                )
                self.database.add(
                    CandidateFactConfirmation(
                        fact_version_id=member.id,
                        confirmation_type="conflict_resolution",
                        confirmed_by_owner_id=1,
                        confirmed_at=now,
                    )
                )
            else:
                member.lifecycle_state = FactState.REVOKED
                member.revoked_at = now
                member.revocation_reason = reason
            self.database.add(
                CandidateFactLifecycleEvent(
                    fact_version_id=member.id,
                    event_type="conflict_resolved",
                    reason=reason,
                    created_at=now,
                )
            )
        conflict.status = "resolved"
        conflict.resolved_at = now
        conflict.resolution_reason = reason
        self.events.record("candidate_fact_conflict_resolved", {"conflict_id": conflict.id})
        self.database.commit()
