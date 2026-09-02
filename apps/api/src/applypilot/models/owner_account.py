from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from applypilot.repositories.database import Base


class OwnerAccount(Base):
    __tablename__ = "owner_account"
    __table_args__ = (CheckConstraint("id = 1", name="ck_owner_account_singleton"),)

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, default=1)
    password_verifier: Mapped[str] = mapped_column(String(512), nullable=False)
    credential_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    password_changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
