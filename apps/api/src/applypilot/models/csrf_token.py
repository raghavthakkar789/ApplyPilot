from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from applypilot.repositories.database import Base

if TYPE_CHECKING:
    from applypilot.models.session import OwnerSession


class SessionCsrfToken(Base):
    __tablename__ = "session_csrf_tokens"

    session_id: Mapped[str] = mapped_column(
        ForeignKey("sessions.id", ondelete="CASCADE"), primary_key=True
    )
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    session: Mapped["OwnerSession"] = relationship(back_populates="csrf_token")
