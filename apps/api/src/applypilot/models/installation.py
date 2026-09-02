from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from applypilot.repositories.database import Base


class Installation(Base):
    __tablename__ = "installation"
    __table_args__ = (CheckConstraint("id = 1", name="ck_installation_singleton"),)

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True, default=1)
    initialized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
