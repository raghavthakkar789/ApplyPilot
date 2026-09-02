from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from applypilot.repositories.database import Base


def uuid_value() -> str:
    return str(uuid4())


class StoredDocument(Base):
    __tablename__ = "stored_documents"
    __table_args__ = (
        UniqueConstraint("sha256", "byte_length", name="uq_stored_document_content"),
        CheckConstraint("byte_length >= 0", name="ck_stored_document_size"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    storage_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    byte_length: Mapped[int] = mapped_column(BigInteger, nullable=False)
    detected_media_type: Mapped[str] = mapped_column(String(100), nullable=False)
    document_format: Mapped[str] = mapped_column(String(12), nullable=False)
    integrity_state: Mapped[str] = mapped_column(String(20), nullable=False, default="verified")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Resume(Base):
    __tablename__ = "resumes"
    __table_args__ = (Index("ix_resumes_owner_trash", "owner_id", "trashed_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    owner_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey("owner_account.id", ondelete="RESTRICT"), nullable=False
    )
    display_name: Mapped[str] = mapped_column(String(160), nullable=False)
    purpose: Mapped[str | None] = mapped_column(String(160))
    current_version_id: Mapped[str | None] = mapped_column(String(36))
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    trashed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    purge_after: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ResumeVersion(Base):
    __tablename__ = "resume_versions"
    __table_args__ = (
        UniqueConstraint("resume_id", "version_number", name="uq_resume_version_number"),
        CheckConstraint(
            "extraction_status IN ('pending','succeeded','failed')",
            name="ck_resume_extraction_status",
        ),
        Index("ix_resume_versions_resume_created", "resume_id", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    resume_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resumes.id", ondelete="RESTRICT"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    document_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stored_documents.id", ondelete="RESTRICT"), nullable=False
    )
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    declared_media_type: Mapped[str] = mapped_column(String(100), nullable=False)
    parser_name: Mapped[str] = mapped_column(String(50), nullable=False)
    parser_version: Mapped[str] = mapped_column(String(50), nullable=False)
    extraction_status: Mapped[str] = mapped_column(String(16), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    superseded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    trashed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    permanently_deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    resume_version_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("resume_versions.id", ondelete="RESTRICT"),
        unique=True,
        nullable=False,
    )
    extracted_text: Mapped[str | None] = mapped_column(Text)
    page_count: Mapped[int | None] = mapped_column(Integer)
    paragraph_count: Mapped[int | None] = mapped_column(Integer)
    segments: Mapped[list[object]] = mapped_column(JSON, nullable=False, default=list)
    warnings: Mapped[list[object]] = mapped_column(JSON, nullable=False, default=list)
    parser_result: Mapped[str] = mapped_column(String(20), nullable=False)
    extracted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    integrity_hash: Mapped[str | None] = mapped_column(String(64))
    failure_category: Mapped[str | None] = mapped_column(String(60))


class ResumeFactCandidate(Base):
    __tablename__ = "resume_fact_candidates"
    __table_args__ = (
        CheckConstraint(
            "review_status IN ('pending','accepted','rejected')",
            name="ck_resume_candidate_review_status",
        ),
        Index("ix_resume_candidates_version_status", "resume_version_id", "review_status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    resume_version_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("resume_versions.id", ondelete="RESTRICT"), nullable=False
    )
    fact_type: Mapped[str] = mapped_column(String(64), nullable=False)
    semantic_key: Mapped[str] = mapped_column(String(160), nullable=False)
    proposed_value: Mapped[object] = mapped_column(JSON, nullable=False)
    evidence_citation: Mapped[str] = mapped_column(String(500), nullable=False)
    extraction_method: Mapped[str] = mapped_column(String(80), nullable=False)
    confidence: Mapped[str | None] = mapped_column(String(16))
    review_status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resulting_fact_identity_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("candidate_fact_identities.id", ondelete="RESTRICT")
    )
    resulting_fact_version_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("candidate_fact_versions.id", ondelete="RESTRICT")
    )


class DocumentLifecycleEvent(Base):
    __tablename__ = "document_lifecycle_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    resume_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("resumes.id", ondelete="RESTRICT")
    )
    resume_version_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("resume_versions.id", ondelete="RESTRICT")
    )
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    outcome: Mapped[str] = mapped_column(String(20), nullable=False)
    metadata_json: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
