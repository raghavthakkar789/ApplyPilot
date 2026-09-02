from dataclasses import dataclass

from fastapi import Cookie, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from applypilot.core.request_security import browser_host_matches
from applypilot.models.owner_account import OwnerAccount
from applypilot.models.session import OwnerSession
from applypilot.repositories.database import get_database_session
from applypilot.repositories.owner_repository import OwnerRepository
from applypilot.services.session_service import SessionService

SESSION_COOKIE = "applypilot_session"


@dataclass(frozen=True)
class AuthenticationContext:
    owner: OwnerAccount
    session: OwnerSession


def client_label(request: Request) -> str | None:
    user_agent = request.headers.get("user-agent", "").lower()
    if not user_agent:
        return None
    for marker, label in (
        ("firefox", "Firefox browser"),
        ("edg/", "Edge browser"),
        ("chrome", "Chrome browser"),
        ("safari", "Safari browser"),
    ):
        if marker in user_agent:
            return label
    return "Local browser"


def require_authentication(
    request: Request,
    database: Session = Depends(get_database_session),
    raw_token: str | None = Cookie(default=None, alias=SESSION_COOKIE),
) -> AuthenticationContext:
    if not browser_host_matches(request):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Request could not be verified."
        )
    if raw_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required."
        )
    owner = OwnerRepository(database).owner()
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required."
        )
    session, _ = SessionService(database).authenticate(raw_token, owner)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required."
        )
    return AuthenticationContext(owner, session)
