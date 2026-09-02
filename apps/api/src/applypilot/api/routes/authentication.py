from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import (
    AuthenticationContext,
    client_label,
    require_authentication,
)
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.api.routes.common import require_public_origin, set_session_cookie
from applypilot.repositories.database import get_database_session
from applypilot.schemas.authentication import AuthenticationResponse, LoginRequest
from applypilot.services.authentication_service import (
    AuthenticationFailed,
    AuthenticationService,
    LoginThrottled,
)
from applypilot.services.session_service import SessionService

router = APIRouter(prefix="/auth", tags=["authentication"])
GENERIC_FAILURE = "Authentication could not be completed."


@router.post("/login", response_model=AuthenticationResponse)
def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    database: Session = Depends(get_database_session),
) -> AuthenticationResponse:
    require_public_origin(request)
    try:
        new_session = AuthenticationService(database).login(payload.password, client_label(request))
    except AuthenticationFailed as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=GENERIC_FAILURE
        ) from error
    except LoginThrottled as error:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=GENERIC_FAILURE,
            headers={"Retry-After": str(error.retry_after)},
        ) from error
    set_session_cookie(response, new_session)
    return AuthenticationResponse(authenticated=True)


@router.get("/status")
def authentication_status(
    _context: AuthenticationContext = Depends(require_authentication),
) -> dict[str, bool]:
    return {"authenticated": True}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    context: AuthenticationContext = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> None:
    SessionService(database).revoke(context.session, "logout", "logout")
    database.commit()
    response.delete_cookie("applypilot_session", path="/")
    response.delete_cookie("applypilot_csrf", path="/")
