from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import require_authentication
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.api.routes.candidate_facts import version_response
from applypilot.repositories.candidate_fact_repository import CandidateFactRepository
from applypilot.repositories.database import get_database_session
from applypilot.schemas.candidate_fact_conflict import (
    ConflictDetailResponse,
    ConflictListResponse,
    ConflictResolutionRequest,
    ConflictSummaryResponse,
)
from applypilot.services.candidate_conflict_service import CandidateConflictService

router = APIRouter(prefix="/candidate-fact-conflicts", tags=["candidate-fact-conflicts"])


@router.get("", response_model=ConflictListResponse, dependencies=[Depends(require_authentication)])
def list_conflicts(database: Session = Depends(get_database_session)) -> ConflictListResponse:
    conflicts = CandidateFactRepository(database).open_conflicts()
    return ConflictListResponse(
        conflicts=[
            ConflictSummaryResponse(
                id=item.id,
                semantic_key=item.semantic_key,
                status=item.status,
                detected_at=item.detected_at,
            )
            for item in conflicts
        ]
    )


@router.get(
    "/{conflict_id}",
    response_model=ConflictDetailResponse,
    dependencies=[Depends(require_authentication)],
)
def read_conflict(
    conflict_id: str, database: Session = Depends(get_database_session)
) -> ConflictDetailResponse:
    repository = CandidateFactRepository(database)
    conflict = repository.conflict(conflict_id)
    if conflict is None:
        raise HTTPException(404, "Conflict not found.")
    return ConflictDetailResponse(
        id=conflict.id,
        semantic_key=conflict.semantic_key,
        status=conflict.status,
        detected_at=conflict.detected_at,
        members=[
            version_response(member, True) for member in repository.conflict_members(conflict.id)
        ],
    )


@router.post("/{conflict_id}/resolve", status_code=204)
def resolve_conflict(
    conflict_id: str,
    request: ConflictResolutionRequest,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> None:
    CandidateConflictService(database).resolve(
        conflict_id, request.selected_version_id, request.reason
    )
