from fastapi import HTTPException, Request, Response, status

from applypilot.api.dependencies.authentication import SESSION_COOKIE, client_label
from applypilot.core.config import get_settings
from applypilot.core.request_security import browser_host_matches
from applypilot.services.session_service import NewSession


def require_browser_host(request: Request) -> None:
    if not browser_host_matches(request):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Request could not be completed."
        )


def require_public_origin(request: Request) -> None:
    require_browser_host(request)
    if request.headers.get("origin") != get_settings().allowed_origin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Request could not be completed."
        )


def set_session_cookie(response: Response, new_session: NewSession) -> None:
    settings = get_settings()
    response.set_cookie(
        key=SESSION_COOKIE,
        value=new_session.raw_session_token,
        max_age=12 * 60 * 60,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="strict",
        path="/",
    )
    response.set_cookie(
        key="applypilot_csrf",
        value=new_session.raw_csrf_token,
        max_age=12 * 60 * 60,
        httponly=False,
        secure=settings.cookie_secure,
        samesite="strict",
        path="/",
    )


__all__ = ["client_label", "require_browser_host", "require_public_origin", "set_session_cookie"]
