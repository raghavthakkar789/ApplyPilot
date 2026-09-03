from sqlalchemy import select
from sqlalchemy.orm import Session

from applypilot.models.candidate_fact import CandidateFactIdentity, CandidateFactVersion
from applypilot.models.candidate_fact_conflict import (
    CandidateFactConflict,
    CandidateFactConflictMember,
)


class CandidateFactRepository:
    def __init__(self, database: Session) -> None:
        self.database = database

    def identities(self) -> list[CandidateFactIdentity]:
        return list(
            self.database.scalars(
                select(CandidateFactIdentity).order_by(CandidateFactIdentity.semantic_key)
            )
        )

    def identity_by_key(
        self, semantic_key: str, scope: str = "*", *, lock: bool = False
    ) -> CandidateFactIdentity | None:
        statement = select(CandidateFactIdentity).where(
            CandidateFactIdentity.owner_id == 1,
            CandidateFactIdentity.semantic_key == semantic_key,
            CandidateFactIdentity.scope == scope,
        )
        if lock:
            statement = statement.with_for_update()
        return self.database.scalar(statement)

    def identity(self, identity_id: str, lock: bool = False) -> CandidateFactIdentity | None:
        statement = select(CandidateFactIdentity).where(CandidateFactIdentity.id == identity_id)
        if lock:
            statement = statement.with_for_update()
        return self.database.scalar(statement)

    def versions(self, identity_id: str) -> list[CandidateFactVersion]:
        return list(
            self.database.scalars(
                select(CandidateFactVersion)
                .where(CandidateFactVersion.fact_identity_id == identity_id)
                .order_by(CandidateFactVersion.version_number.desc())
            )
        )

    def version(self, version_id: str, lock: bool = False) -> CandidateFactVersion | None:
        statement = select(CandidateFactVersion).where(CandidateFactVersion.id == version_id)
        if lock:
            statement = statement.with_for_update()
        return self.database.scalar(statement)

    def active_by_key(self, key: str) -> list[tuple[CandidateFactIdentity, CandidateFactVersion]]:
        statement = (
            select(CandidateFactIdentity, CandidateFactVersion)
            .join(CandidateFactVersion)
            .where(
                CandidateFactIdentity.semantic_key == key,
                CandidateFactVersion.superseded_at.is_(None),
                CandidateFactVersion.lifecycle_state != "revoked",
            )
        )
        return list(self.database.execute(statement).tuples())

    def open_conflicts(self) -> list[CandidateFactConflict]:
        return list(
            self.database.scalars(
                select(CandidateFactConflict)
                .where(CandidateFactConflict.status == "open")
                .order_by(CandidateFactConflict.detected_at.desc())
            )
        )

    def conflict(self, conflict_id: str) -> CandidateFactConflict | None:
        return self.database.get(CandidateFactConflict, conflict_id)

    def conflict_members(self, conflict_id: str) -> list[CandidateFactVersion]:
        return list(
            self.database.scalars(
                select(CandidateFactVersion)
                .join(
                    CandidateFactConflictMember,
                    CandidateFactConflictMember.fact_version_id == CandidateFactVersion.id,
                )
                .where(CandidateFactConflictMember.conflict_id == conflict_id)
            )
        )
