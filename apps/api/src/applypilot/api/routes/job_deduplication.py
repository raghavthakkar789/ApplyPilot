from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import require_authentication
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.repositories.database import get_database_session
from applypilot.repositories.job_repository import JobRepository
from applypilot.schemas.job import DeduplicationCandidateResponse, DeduplicationResolution
from applypilot.services.job_deduplication_service import JobDeduplicationService

router = APIRouter(prefix="/job-deduplication", tags=["job-deduplication"])


@router.get(
    "",
    response_model=list[DeduplicationCandidateResponse],
    dependencies=[Depends(require_authentication)],
)
def list_candidates(
    database: Session = Depends(get_database_session),
) -> list[DeduplicationCandidateResponse]:
    return [
        DeduplicationCandidateResponse.model_validate(item, from_attributes=True)
        for item in JobRepository(database).deduplication_candidates()
    ]


def resolve_candidate(
    candidate_id: str,
    value: DeduplicationResolution,
    merge: bool,
    database: Session,
) -> DeduplicationCandidateResponse:
    item = JobDeduplicationService(database).resolve(candidate_id, merge, value.reason)
    return DeduplicationCandidateResponse.model_validate(item, from_attributes=True)


@router.post("/{candidate_id}/merge", response_model=DeduplicationCandidateResponse)
def merge_candidate(
    candidate_id: str,
    value: DeduplicationResolution,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> DeduplicationCandidateResponse:
    return resolve_candidate(candidate_id, value, True, database)


@router.post("/{candidate_id}/split", response_model=DeduplicationCandidateResponse)
def split_candidate(
    candidate_id: str,
    value: DeduplicationResolution,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> DeduplicationCandidateResponse:
    return resolve_candidate(candidate_id, value, False, database)
