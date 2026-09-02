from datetime import UTC, datetime

from fastapi import Depends, Header, HTTPException, Request, status
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import AuthenticationContext, require_authentication
from applypilot.core.config import get_settings
from applypilot.core.csrf import CSRF_HEADER, csrf_matches
from applypilot.repositories.database import get_database_session
from applypilot.repositories.session_repository import SessionRepository


def require_csrf(
    request: Request,
    context: AuthenticationContext = Depends(require_authentication),
    database: Session = Depends(get_database_session),
    csrf_token: str | None = Header(default=None, alias=CSRF_HEADER),
) -> AuthenticationContext:
    if request.headers.get("origin") != get_settings().allowed_origin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Request could not be verified."
        )
    verifier = SessionRepository(database).csrf(context.session.id)
    if (
        csrf_token is None
        or verifier is None
        or datetime.now(UTC) >= verifier.expires_at
        or not csrf_matches(csrf_token, verifier.token_hash)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Request could not be verified."
        )
    return context
