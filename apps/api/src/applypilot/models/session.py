from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from applypilot.repositories.database import Base

if TYPE_CHECKING:
    from applypilot.models.csrf_token import SessionCsrfToken


class OwnerSession(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_sessions_active_activity", "revoked_at", "last_activity_at"),
        Index("ix_sessions_token_hash", "token_hash", unique=True),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_id: Mapped[int] = mapped_column(ForeignKey("owner_account.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_activity_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    idle_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    absolute_expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revocation_reason: Mapped[str | None] = mapped_column(String(64))
    credential_version: Mapped[int] = mapped_column(Integer, nullable=False)
    client_label: Mapped[str | None] = mapped_column(String(80))
    csrf_token: Mapped["SessionCsrfToken"] = relationship(
        back_populates="session", cascade="all, delete-orphan", uselist=False
    )
