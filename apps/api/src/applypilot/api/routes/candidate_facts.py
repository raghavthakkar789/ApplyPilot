from datetime import UTC, datetime
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import require_authentication
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.models.candidate_fact import CandidateFactIdentity, CandidateFactVersion
from applypilot.repositories.candidate_fact_repository import CandidateFactRepository
from applypilot.repositories.database import get_database_session
from applypilot.schemas.candidate_fact import (
    FactCreateRequest,
    FactDetailResponse,
    FactEditRequest,
    FactListResponse,
    FactReasonRequest,
    FactStateValue,
    FactSummaryResponse,
    FactVersionResponse,
)
from applypilot.services.candidate_fact_service import CandidateFactService

router = APIRouter(prefix="/candidate-facts", tags=["candidate-facts"])


def version_response(
    version: CandidateFactVersion, current: bool, broad: bool = False
) -> FactVersionResponse:
    hide_value = broad and version.sensitivity in {"private", "eligibility", "highly_sensitive"}
    state = version.lifecycle_state
    if (
        state == "verified"
        and version.reconfirmation_due_at is not None
        and datetime.now(UTC) >= version.reconfirmation_due_at
    ):
        state = "stale"
    return FactVersionResponse(
        id=version.id,
        version_number=version.version_number,
        value=None if hide_value else version.typed_value,
        lifecycle_state=cast(FactStateValue, state),
        source_type=version.source_type,
        source_reference=version.source_reference,
        source_version=version.source_version,
        evidence_citation=version.evidence_citation,
        created_at=version.created_at,
        owner_confirmed_at=version.owner_confirmed_at,
        reconfirmation_policy=version.reconfirmation_policy,
        confirmation_due_at=version.reconfirmation_due_at,
        sensitivity=version.sensitivity,
        current=current,
    )


def summary(
    identity: CandidateFactIdentity, versions: list[CandidateFactVersion]
) -> FactSummaryResponse:
    current = versions[0]
    return FactSummaryResponse(
        identity_id=identity.id,
        fact_type=identity.fact_type,
        semantic_key=identity.semantic_key,
        scope=identity.scope,
        current_version=version_response(current, True, broad=True),
    )


@router.get("", response_model=FactListResponse, dependencies=[Depends(require_authentication)])
def list_facts(database: Session = Depends(get_database_session)) -> FactListResponse:
    repository = CandidateFactRepository(database)
    facts = []
    for identity in repository.identities():
        versions = repository.versions(identity.id)
        if versions:
            facts.append(summary(identity, versions))
    return FactListResponse(facts=facts)


@router.get(
    "/{identity_id}",
    response_model=FactDetailResponse,
    dependencies=[Depends(require_authentication)],
)
def read_fact(
    identity_id: str, database: Session = Depends(get_database_session)
) -> FactDetailResponse:
    repository = CandidateFactRepository(database)
    identity = repository.identity(identity_id)
    if identity is None:
        raise HTTPException(404, "Fact not found.")
    versions = repository.versions(identity.id)
    item = summary(identity, versions)
    return FactDetailResponse(
        **item.model_dump(),
        versions=[version_response(version, index == 0) for index, version in enumerate(versions)],
    )


@router.post("", response_model=FactSummaryResponse, status_code=status.HTTP_201_CREATED)
def create_fact(
    request: FactCreateRequest,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> FactSummaryResponse:
    identity, _ = CandidateFactService(database).create(request)
    return summary(identity, CandidateFactRepository(database).versions(identity.id))


@router.post("/{identity_id}/versions", response_model=FactSummaryResponse)
def edit_fact(
    identity_id: str,
    request: FactEditRequest,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> FactSummaryResponse:
    identity, _ = CandidateFactService(database).edit(identity_id, request)
    return summary(identity, CandidateFactRepository(database).versions(identity.id))


@router.post("/versions/{version_id}/verify", response_model=FactVersionResponse)
def verify_fact(
    version_id: str,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> FactVersionResponse:
    return version_response(CandidateFactService(database).verify(version_id), True)


@router.post("/versions/{version_id}/reconfirm", response_model=FactVersionResponse)
def reconfirm_fact(
    version_id: str,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> FactVersionResponse:
    return version_response(CandidateFactService(database).verify(version_id, reconfirm=True), True)


@router.post("/versions/{version_id}/revoke", response_model=FactVersionResponse)
def revoke_fact(
    version_id: str,
    request: FactReasonRequest,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> FactVersionResponse:
    return version_response(CandidateFactService(database).revoke(version_id, request.reason), True)
