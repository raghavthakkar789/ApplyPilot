from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from applypilot.repositories.database import Base


class CandidateFactConflict(Base):
    __tablename__ = "candidate_fact_conflicts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    semantic_key: Mapped[str] = mapped_column(String(160), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="open")
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution_reason: Mapped[str | None] = mapped_column(String(240))


class CandidateFactConflictMember(Base):
    __tablename__ = "candidate_fact_conflict_members"
    __table_args__ = (UniqueConstraint("conflict_id", "fact_version_id"),)

    conflict_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidate_fact_conflicts.id"), primary_key=True
    )
    fact_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidate_fact_versions.id"), primary_key=True
    )
