from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import require_authentication
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.repositories.database import get_database_session
from applypilot.repositories.resume_repository import ResumeRepository
from applypilot.schemas.resume_fact_candidate import (
    CandidateAcceptanceResponse,
    ResumeFactCandidateListResponse,
    ResumeFactCandidateResponse,
)
from applypilot.services.resume_candidate_service import ResumeCandidateService

router = APIRouter(tags=["resume-fact-candidates"])


def candidate_response(candidate: object) -> ResumeFactCandidateResponse:
    return ResumeFactCandidateResponse.model_validate(candidate, from_attributes=True)


@router.get(
    "/resume-versions/{version_id}/fact-candidates",
    response_model=ResumeFactCandidateListResponse,
    dependencies=[Depends(require_authentication)],
)
def list_candidates(
    version_id: str, database: Session = Depends(get_database_session)
) -> ResumeFactCandidateListResponse:
    return ResumeFactCandidateListResponse(
        candidates=[
            candidate_response(item) for item in ResumeRepository(database).candidates(version_id)
        ]
    )


@router.post(
    "/resume-fact-candidates/{candidate_id}/accept",
    response_model=CandidateAcceptanceResponse,
)
def accept_candidate(
    candidate_id: str,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> CandidateAcceptanceResponse:
    identity_id, version_id = ResumeCandidateService(database).accept(candidate_id)
    return CandidateAcceptanceResponse(
        candidate_id=candidate_id,
        fact_identity_id=identity_id,
        fact_version_id=version_id,
    )


@router.post("/resume-fact-candidates/{candidate_id}/reject", status_code=204)
def reject_candidate(
    candidate_id: str,
    _context: object = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> None:
    ResumeCandidateService(database).reject(candidate_id)
