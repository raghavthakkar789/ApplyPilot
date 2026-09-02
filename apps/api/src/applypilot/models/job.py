from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from applypilot.repositories.database import Base


def uuid_value() -> str:
    return str(uuid4())


class AtsRegistryEntry(Base):
    __tablename__ = "ats_registry_entries"
    __table_args__ = (UniqueConstraint("provider", "board_identifier", name="uq_registry_board"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    employer_name: Mapped[str] = mapped_column(String(160), nullable=False)
    employer_domain: Mapped[str] = mapped_column(String(253), nullable=False)
    board_identifier: Mapped[str] = mapped_column(String(160), nullable=False)
    careers_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    state: Mapped[str] = mapped_column(String(24), nullable=False, default="pending_review")
    verification_method: Mapped[str] = mapped_column(String(80), nullable=False)
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_failure_category: Mapped[str | None] = mapped_column(String(80))
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class SourceSyncRun(Base):
    __tablename__ = "source_sync_runs"
    __table_args__ = (Index("ix_sync_provider_started", "provider", "started_at"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    registry_entry_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("ats_registry_entries.id", ondelete="RESTRICT")
    )
    status: Mapped[str] = mapped_column(String(24), nullable=False)
    records_seen: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_changed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    safe_failure_category: Mapped[str | None] = mapped_column(String(80))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RawJobRecord(Base):
    __tablename__ = "raw_job_records"
    __table_args__ = (
        UniqueConstraint(
            "provider", "board_identifier", "source_record_id", name="uq_raw_job_identity"
        ),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)
    board_identifier: Mapped[str | None] = mapped_column(String(160))
    source_record_id: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_job_id: Mapped[str | None] = mapped_column(String(36))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    missing_observations: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class RawJobRecordVersion(Base):
    __tablename__ = "raw_job_record_versions"
    __table_args__ = (
        UniqueConstraint("raw_job_record_id", "payload_hash", name="uq_raw_payload_hash"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    raw_job_record_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("raw_job_records.id", ondelete="RESTRICT"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    adapter_version: Mapped[str] = mapped_column(String(20), nullable=False)
    retrieved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CanonicalJob(Base):
    __tablename__ = "canonical_jobs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    current_version_id: Mapped[str | None] = mapped_column(String(36))
    saved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class CanonicalJobVersion(Base):
    __tablename__ = "canonical_job_versions"
    __table_args__ = (
        UniqueConstraint("canonical_job_id", "version_number", name="uq_canonical_job_version"),
        Index("ix_job_version_search", "employer", "title"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    canonical_job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("canonical_jobs.id", ondelete="RESTRICT"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    employer: Mapped[str] = mapped_column(String(160), nullable=False)
    description_text: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_data: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    normalization_warnings: Mapped[list[object]] = mapped_column(JSON, nullable=False, default=list)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    freshness_state: Mapped[str] = mapped_column(String(24), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class JobSourceLink(Base):
    __tablename__ = "job_source_links"
    __table_args__ = (
        UniqueConstraint("canonical_job_id", "raw_job_record_id", name="uq_job_source_link"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    canonical_job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("canonical_jobs.id", ondelete="RESTRICT"), nullable=False
    )
    raw_job_record_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("raw_job_records.id", ondelete="RESTRICT"), nullable=False
    )
    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    application_url: Mapped[str | None] = mapped_column(String(2048))
    attribution: Mapped[str] = mapped_column(String(160), nullable=False)
    linked_reason: Mapped[str] = mapped_column(String(80), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class JobDeduplicationCandidate(Base):
    __tablename__ = "job_deduplication_candidates"
    __table_args__ = (
        UniqueConstraint("left_job_id", "right_job_id", name="uq_job_deduplication_pair"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    left_job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("canonical_jobs.id", ondelete="RESTRICT"), nullable=False
    )
    right_job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("canonical_jobs.id", ondelete="RESTRICT"), nullable=False
    )
    reasons: Mapped[list[object]] = mapped_column(JSON, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    owner_reason: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class ManualJobRecord(Base):
    __tablename__ = "manual_job_records"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=uuid_value)
    canonical_job_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("canonical_jobs.id", ondelete="RESTRICT"), nullable=False
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    owner_input: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
