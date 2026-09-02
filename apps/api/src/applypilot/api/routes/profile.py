from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import require_authentication
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.repositories.database import get_database_session
from applypilot.schemas.profile import ProfileResponse, ProfileSections
from applypilot.services.candidate_profile_service import CandidateProfileService

router = APIRouter(prefix="/profile", tags=["candidate-profile"])


def response(profile: object | None) -> ProfileResponse:
    from applypilot.models.candidate_profile import CandidateProfile

    if profile is None:
        return ProfileResponse(sections=ProfileSections(), created_at=None, updated_at=None)
    assert isinstance(profile, CandidateProfile)
    return ProfileResponse(
        sections=ProfileSections.model_validate(profile.sections),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


@router.get("", response_model=ProfileResponse, dependencies=[Depends(require_authentication)])
def read_profile(database: Session = Depends(get_database_session)) -> ProfileResponse:
    return response(CandidateProfileService(database).get())


@router.put("", response_model=ProfileResponse, dependencies=[Depends(require_csrf)])
def update_profile(
    sections: ProfileSections, database: Session = Depends(get_database_session)
) -> ProfileResponse:
    return response(CandidateProfileService(database).update(sections))
