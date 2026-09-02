from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import client_label
from applypilot.api.routes.common import (
    require_browser_host,
    require_public_origin,
    set_session_cookie,
)
from applypilot.core.security import PasswordPolicyError
from applypilot.repositories.database import get_database_session
from applypilot.repositories.security_repository import SecurityRepository
from applypilot.schemas.authentication import AuthenticationResponse
from applypilot.schemas.initialization import InitializationRequest, InitializationStatus
from applypilot.services.initialization_service import (
    InitializationService,
    InitializationThrottled,
    InitializationUnavailable,
)

router = APIRouter(prefix="/initialization", tags=["initialization"])


@router.get("/status", response_model=InitializationStatus)
def initialization_status(
    request: Request,
    database: Session = Depends(get_database_session),
) -> InitializationStatus:
    require_browser_host(request)
    return InitializationStatus(required=InitializationService(database).is_required())


@router.post("", response_model=AuthenticationResponse, status_code=status.HTTP_201_CREATED)
def initialize(
    payload: InitializationRequest,
    request: Request,
    response: Response,
    database: Session = Depends(get_database_session),
) -> AuthenticationResponse:
    require_public_origin(request)
    try:
        new_session = InitializationService(database).initialize(
            payload.password, payload.password_confirmation, client_label(request)
        )
    except InitializationUnavailable as error:
        SecurityRepository(database).record("initialization_failure", {"reason": "unavailable"})
        database.commit()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found.") from error
    except InitializationThrottled as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Request could not be completed.",
            headers={"Retry-After": str(error.retry_after)},
        ) from error
    except (PasswordPolicyError, ValueError) as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    set_session_cookie(response, new_session)
    return AuthenticationResponse(authenticated=True)
