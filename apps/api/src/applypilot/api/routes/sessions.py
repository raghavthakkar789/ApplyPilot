from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from applypilot.api.dependencies.authentication import AuthenticationContext, require_authentication
from applypilot.api.dependencies.csrf import require_csrf
from applypilot.repositories.database import get_database_session
from applypilot.repositories.session_repository import SessionRepository
from applypilot.schemas.session import RevocationResponse, SessionListResponse, SessionResponse
from applypilot.services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])


def serialize_session(session: object, current_id: str) -> SessionResponse:
    from applypilot.models.session import OwnerSession

    assert isinstance(session, OwnerSession)
    return SessionResponse(
        id=session.id,
        created_at=session.created_at,
        last_activity_at=session.last_activity_at,
        idle_expires_at=session.idle_expires_at,
        absolute_expires_at=session.absolute_expires_at,
        client_label=session.client_label,
        current=session.id == current_id,
    )


@router.get("/current", response_model=SessionResponse)
def current_session(
    context: AuthenticationContext = Depends(require_authentication),
) -> SessionResponse:
    return serialize_session(context.session, context.session.id)


@router.get("", response_model=SessionListResponse)
def list_sessions(
    context: AuthenticationContext = Depends(require_authentication),
    database: Session = Depends(get_database_session),
) -> SessionListResponse:
    from datetime import UTC, datetime

    sessions = SessionRepository(database).active(datetime.now(UTC))
    return SessionListResponse(
        sessions=[serialize_session(session, context.session.id) for session in sessions]
    )


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_session(
    session_id: str,
    context: AuthenticationContext = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> None:
    session = SessionRepository(database).get(session_id)
    if session is None or session.revoked_at is not None:
        raise HTTPException(status_code=404, detail="Session not found.")
    SessionService(database).revoke(session, "owner_revocation", "individual_revocation")
    database.commit()


@router.post("/revoke-others", response_model=RevocationResponse)
def revoke_other_sessions(
    context: AuthenticationContext = Depends(require_csrf),
    database: Session = Depends(get_database_session),
) -> RevocationResponse:
    count = SessionService(database).revoke_others(context.session)
    database.commit()
    return RevocationResponse(revoked_count=count)
