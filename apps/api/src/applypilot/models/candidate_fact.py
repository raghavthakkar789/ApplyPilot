from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from applypilot.repositories.database import Base


class CandidateFactIdentity(Base):
    __tablename__ = "candidate_fact_identities"
    __table_args__ = (
        UniqueConstraint("owner_id", "semantic_key", "scope", name="uq_fact_identity_key_scope"),
        Index("ix_fact_identity_semantic_scope", "semantic_key", "scope"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    owner_id: Mapped[int] = mapped_column(SmallInteger, ForeignKey("owner_account.id"))
    fact_type: Mapped[str] = mapped_column(String(64), nullable=False)
    semantic_key: Mapped[str] = mapped_column(String(160), nullable=False)
    scope: Mapped[str] = mapped_column(String(160), nullable=False, default="*")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CandidateFactVersion(Base):
    __tablename__ = "candidate_fact_versions"
    __table_args__ = (
        UniqueConstraint("fact_identity_id", "version_number", name="uq_fact_version_number"),
        CheckConstraint(
            "lifecycle_state IN ('unverified','verified','stale','conflicted','revoked')",
            name="ck_fact_version_state",
        ),
        Index("ix_fact_version_current", "fact_identity_id", "superseded_at", "lifecycle_state"),
        Index("ix_fact_version_reconfirmation", "reconfirmation_due_at", "lifecycle_state"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    fact_identity_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidate_fact_identities.id"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    typed_value: Mapped[object] = mapped_column(JSON, nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(String(16), nullable=False)
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_reference: Mapped[str | None] = mapped_column(String(240))
    source_version: Mapped[str | None] = mapped_column(String(120))
    evidence_citation: Mapped[str | None] = mapped_column(String(500))
    extraction_method: Mapped[str | None] = mapped_column(String(80))
    extraction_confidence: Mapped[str | None] = mapped_column(String(16))
    owner_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    supersession_reason: Mapped[str | None] = mapped_column(String(240))
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    revocation_reason: Mapped[str | None] = mapped_column(String(240))
    sensitivity: Mapped[str] = mapped_column(String(32), nullable=False)
    reconfirmation_policy: Mapped[str] = mapped_column(String(40), nullable=False)
    reconfirmation_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    integrity_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class CandidateFactConfirmation(Base):
    __tablename__ = "candidate_fact_confirmations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    fact_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidate_fact_versions.id"), nullable=False
    )
    confirmation_type: Mapped[str] = mapped_column(String(24), nullable=False)
    confirmed_by_owner_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("owner_account.id"), nullable=False
    )
    confirmed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CandidateFactLifecycleEvent(Base):
    __tablename__ = "candidate_fact_lifecycle_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    fact_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidate_fact_versions.id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(240))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CandidateFactEvidence(Base):
    __tablename__ = "candidate_fact_evidence"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    fact_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("candidate_fact_versions.id"), nullable=False
    )
    source_type: Mapped[str] = mapped_column(String(32), nullable=False)
    source_identifier: Mapped[str | None] = mapped_column(String(240))
    source_version: Mapped[str | None] = mapped_column(String(120))
    citation: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
