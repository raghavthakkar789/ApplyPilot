import hashlib
import json
from datetime import UTC, datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from applypilot.domain.candidate_fact import PROTECTED_FACT_TYPES, FactState
from applypilot.domain.fact_scope import scopes_overlap
from applypilot.domain.reconfirmation import confirmation_due_at
from applypilot.models.candidate_fact import (
    CandidateFactConfirmation,
    CandidateFactEvidence,
    CandidateFactIdentity,
    CandidateFactLifecycleEvent,
    CandidateFactVersion,
)
from applypilot.models.candidate_fact_conflict import (
    CandidateFactConflict,
    CandidateFactConflictMember,
)
from applypilot.repositories.candidate_fact_repository import CandidateFactRepository
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.schemas.candidate_fact import FactCreateRequest, FactEditRequest


def value_hash(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


class CandidateFactService:
    def __init__(self, database: Session) -> None:
        self.database = database
        self.repository = CandidateFactRepository(database)
        self.events = SecurityRepository(database)

    def create(
        self, request: FactCreateRequest, *, commit: bool = True
    ) -> tuple[CandidateFactIdentity, CandidateFactVersion]:
        if request.fact_type in PROTECTED_FACT_TYPES or request.sensitivity == "highly_sensitive":
            raise HTTPException(422, "Protected demographic facts are not collected in Profile.")
        now = datetime.now(UTC)
        identity = self.database.scalar(
            select(CandidateFactIdentity).where(
                CandidateFactIdentity.owner_id == 1,
                CandidateFactIdentity.semantic_key == request.semantic_key,
                CandidateFactIdentity.scope == request.scope,
            )
        )
        if identity is None:
            identity = CandidateFactIdentity(
                owner_id=1,
                fact_type=request.fact_type,
                semantic_key=request.semantic_key,
                scope=request.scope,
                created_at=now,
            )
            self.database.add(identity)
            self.database.flush()
            self.events.record("candidate_fact_identity_created", {"fact_identity_id": identity.id})
        else:
            raise HTTPException(409, "Fact identity already exists; create a new version instead.")
        versions = self.repository.versions(identity.id)
        version = self._new_version(identity, request, len(versions) + 1, now)
        self._detect_conflicts(identity, version, now)
        if commit:
            self.database.commit()
        return identity, version

    def edit(
        self, identity_id: str, request: FactEditRequest, *, commit: bool = True
    ) -> tuple[CandidateFactIdentity, CandidateFactVersion]:
        identity = self.repository.identity(identity_id, lock=True)
        if identity is None:
            raise HTTPException(404, "Fact not found.")
        versions = self.repository.versions(identity.id)
        now = datetime.now(UTC)
        if versions and versions[0].superseded_at is None:
            versions[0].superseded_at = now
            versions[0].supersession_reason = request.reason
            if versions[0].lifecycle_state == FactState.VERIFIED:
                versions[0].lifecycle_state = FactState.STALE
                self._lifecycle(versions[0], "fact_marked_stale", request.reason, now)
        version = self._new_version(identity, request, versions[0].version_number + 1, now)
        self._detect_conflicts(identity, version, now)
        if commit:
            self.database.commit()
        return identity, version

    def verify(self, version_id: str, reconfirm: bool = False) -> CandidateFactVersion:
        version = self.repository.version(version_id, lock=True)
        if version is None:
            raise HTTPException(404, "Fact version not found.")
        allowed = {FactState.STALE, FactState.VERIFIED} if reconfirm else {FactState.UNVERIFIED}
        if version.lifecycle_state not in allowed or version.superseded_at is not None:
            raise HTTPException(409, "This fact version is not eligible for confirmation.")
        if version.reconfirmation_policy in {"per_application", "per_destination_attempt"}:
            raise HTTPException(409, "This fact requires an exact future application context.")
        now = datetime.now(UTC)
        version.lifecycle_state = FactState.VERIFIED
        version.owner_confirmed_at = now
        version.reconfirmation_due_at = confirmation_due_at(version.reconfirmation_policy, now)
        confirmation_type = "reconfirmation" if reconfirm else "verification"
        self.database.add(
            CandidateFactConfirmation(
                fact_version_id=version.id,
                confirmation_type=confirmation_type,
                confirmed_by_owner_id=1,
                confirmed_at=now,
            )
        )
        self._lifecycle(version, f"fact_{confirmation_type}", None, now)
        self.events.record(f"candidate_fact_{confirmation_type}", {"fact_version_id": version.id})
        self.database.commit()
        return version

    def revoke(self, version_id: str, reason: str) -> CandidateFactVersion:
        version = self.repository.version(version_id, lock=True)
        if version is None:
            raise HTTPException(404, "Fact version not found.")
        if version.lifecycle_state == FactState.REVOKED:
            raise HTTPException(409, "Fact version is already revoked.")
        now = datetime.now(UTC)
        version.lifecycle_state = FactState.REVOKED
        version.revoked_at = now
        version.revocation_reason = reason
        self._lifecycle(version, "fact_revoked", reason, now)
        self.events.record("candidate_fact_revoked", {"fact_version_id": version.id})
        self.database.commit()
        return version

    def _new_version(
        self,
        identity: CandidateFactIdentity,
        request: FactCreateRequest,
        number: int,
        now: datetime,
    ) -> CandidateFactVersion:
        version = CandidateFactVersion(
            fact_identity_id=identity.id,
            version_number=number,
            typed_value=request.value,
            lifecycle_state=FactState.UNVERIFIED,
            source_type=request.source_type,
            source_reference=request.source_reference,
            source_version=request.source_version,
            evidence_citation=request.evidence_citation,
            extraction_method=request.extraction_method,
            extraction_confidence=request.extraction_confidence,
            created_at=now,
            sensitivity=request.sensitivity,
            reconfirmation_policy=request.reconfirmation_policy,
            integrity_hash=value_hash(request.value),
        )
        self.database.add(version)
        self.database.flush()
        if request.evidence_citation or request.source_reference:
            self.database.add(
                CandidateFactEvidence(
                    fact_version_id=version.id,
                    source_type=request.source_type,
                    source_identifier=request.source_reference,
                    source_version=request.source_version,
                    citation=request.evidence_citation,
                    created_at=now,
                )
            )
        self._lifecycle(version, "fact_version_created", None, now)
        self.events.record("candidate_fact_version_created", {"fact_version_id": version.id})
        return version

    def _detect_conflicts(
        self, identity: CandidateFactIdentity, version: CandidateFactVersion, now: datetime
    ) -> None:
        for other_identity, other in self.repository.active_by_key(identity.semantic_key):
            if other.id == version.id or other.integrity_hash == version.integrity_hash:
                continue
            if not scopes_overlap(identity.scope, other_identity.scope):
                continue
            conflict = CandidateFactConflict(
                semantic_key=identity.semantic_key, status="open", detected_at=now
            )
            self.database.add(conflict)
            self.database.flush()
            self.database.add_all(
                [
                    CandidateFactConflictMember(conflict_id=conflict.id, fact_version_id=other.id),
                    CandidateFactConflictMember(
                        conflict_id=conflict.id, fact_version_id=version.id
                    ),
                ]
            )
            other.lifecycle_state = FactState.CONFLICTED
            version.lifecycle_state = FactState.CONFLICTED
            self._lifecycle(other, "conflict_detected", None, now)
            self._lifecycle(version, "conflict_detected", None, now)
            self.events.record("candidate_fact_conflict_detected", {"conflict_id": conflict.id})
            break

    def _lifecycle(
        self, version: CandidateFactVersion, event_type: str, reason: str | None, now: datetime
    ) -> None:
        self.database.add(
            CandidateFactLifecycleEvent(
                fact_version_id=version.id,
                event_type=event_type,
                reason=reason,
                created_at=now,
            )
        )


def commit_with_concurrency_error(database: Session) -> None:
    try:
        database.commit()
    except IntegrityError as error:
        database.rollback()
        raise HTTPException(409, "The fact changed concurrently. Please reload.") from error
