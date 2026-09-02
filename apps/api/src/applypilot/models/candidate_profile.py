from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, DateTime, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from applypilot.repositories.database import Base


class CandidateProfile(Base):
    __tablename__ = "candidate_profiles"
    __table_args__ = (CheckConstraint("owner_id = 1", name="ck_candidate_profile_singleton"),)

    owner_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("owner_account.id"), primary_key=True
    )
    sections: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
