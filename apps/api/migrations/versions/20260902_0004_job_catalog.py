"""Add the approved read-only job catalog.

Revision ID: 20260902_0004
Revises: 20260902_0003
"""
# ruff: noqa: E501

from collections.abc import Sequence

from alembic import op

revision: str = "20260902_0004"
down_revision: str | None = "20260902_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("""
    CREATE TABLE ats_registry_entries (id varchar(36) PRIMARY KEY, provider varchar(20) NOT NULL CHECK (provider IN ('greenhouse','lever','ashby')), employer_name varchar(160) NOT NULL, employer_domain varchar(253) NOT NULL, board_identifier varchar(160) NOT NULL, careers_url varchar(2048) NOT NULL, state varchar(24) NOT NULL, verification_method varchar(80) NOT NULL, verified_at timestamptz, last_success_at timestamptz, last_failure_category varchar(80), enabled boolean NOT NULL DEFAULT false, created_at timestamptz NOT NULL, updated_at timestamptz NOT NULL, CONSTRAINT uq_registry_board UNIQUE(provider, board_identifier));
    CREATE TABLE source_sync_runs (id varchar(36) PRIMARY KEY, provider varchar(20) NOT NULL, registry_entry_id varchar(36) REFERENCES ats_registry_entries(id) ON DELETE RESTRICT, status varchar(24) NOT NULL, records_seen integer NOT NULL DEFAULT 0, records_changed integer NOT NULL DEFAULT 0, safe_failure_category varchar(80), started_at timestamptz NOT NULL, finished_at timestamptz);
    CREATE INDEX ix_sync_provider_started ON source_sync_runs(provider, started_at);
    CREATE TABLE raw_job_records (id varchar(36) PRIMARY KEY, provider varchar(20) NOT NULL, board_identifier varchar(160), source_record_id varchar(255) NOT NULL, canonical_job_id varchar(36), created_at timestamptz NOT NULL, last_seen_at timestamptz NOT NULL, missing_observations integer NOT NULL DEFAULT 0, CONSTRAINT uq_raw_job_identity UNIQUE NULLS NOT DISTINCT(provider, board_identifier, source_record_id));
    CREATE TABLE raw_job_record_versions (id varchar(36) PRIMARY KEY, raw_job_record_id varchar(36) NOT NULL REFERENCES raw_job_records(id) ON DELETE RESTRICT, version_number integer NOT NULL, payload json NOT NULL, payload_hash varchar(64) NOT NULL, adapter_version varchar(20) NOT NULL, retrieved_at timestamptz NOT NULL, CONSTRAINT uq_raw_payload_hash UNIQUE(raw_job_record_id, payload_hash), CONSTRAINT uq_raw_version UNIQUE(raw_job_record_id, version_number));
    CREATE TABLE canonical_jobs (id varchar(36) PRIMARY KEY, current_version_id varchar(36), saved boolean NOT NULL DEFAULT false, archived_at timestamptz, created_at timestamptz NOT NULL);
    CREATE TABLE canonical_job_versions (id varchar(36) PRIMARY KEY, canonical_job_id varchar(36) NOT NULL REFERENCES canonical_jobs(id) ON DELETE RESTRICT, version_number integer NOT NULL, title varchar(255) NOT NULL, employer varchar(160) NOT NULL, description_text text NOT NULL, normalized_data json NOT NULL, normalization_warnings json NOT NULL, content_hash varchar(64) NOT NULL, freshness_state varchar(24) NOT NULL, created_at timestamptz NOT NULL, CONSTRAINT uq_canonical_job_version UNIQUE(canonical_job_id, version_number));
    CREATE INDEX ix_job_version_search ON canonical_job_versions(employer, title);
    ALTER TABLE canonical_jobs ADD CONSTRAINT fk_canonical_current_version FOREIGN KEY(current_version_id) REFERENCES canonical_job_versions(id) ON DELETE RESTRICT;
    ALTER TABLE raw_job_records ADD CONSTRAINT fk_raw_canonical_job FOREIGN KEY(canonical_job_id) REFERENCES canonical_jobs(id) ON DELETE RESTRICT;
    CREATE TABLE job_source_links (id varchar(36) PRIMARY KEY, canonical_job_id varchar(36) NOT NULL REFERENCES canonical_jobs(id) ON DELETE RESTRICT, raw_job_record_id varchar(36) NOT NULL REFERENCES raw_job_records(id) ON DELETE RESTRICT, source_url varchar(2048) NOT NULL, application_url varchar(2048), attribution varchar(160) NOT NULL, linked_reason varchar(80) NOT NULL, created_at timestamptz NOT NULL, CONSTRAINT uq_job_source_link UNIQUE(canonical_job_id, raw_job_record_id));
    CREATE TABLE job_deduplication_candidates (id varchar(36) PRIMARY KEY, left_job_id varchar(36) NOT NULL REFERENCES canonical_jobs(id) ON DELETE RESTRICT, right_job_id varchar(36) NOT NULL REFERENCES canonical_jobs(id) ON DELETE RESTRICT, reasons json NOT NULL, status varchar(20) NOT NULL, owner_reason varchar(500), created_at timestamptz NOT NULL, resolved_at timestamptz, CONSTRAINT uq_job_deduplication_pair UNIQUE (left_job_id, right_job_id), CONSTRAINT ck_job_deduplication_distinct CHECK (left_job_id <> right_job_id));
    CREATE TABLE manual_job_records (id varchar(36) PRIMARY KEY, canonical_job_id varchar(36) NOT NULL REFERENCES canonical_jobs(id) ON DELETE RESTRICT, version_number integer NOT NULL, owner_input json NOT NULL, created_at timestamptz NOT NULL, CONSTRAINT uq_manual_job_version UNIQUE(canonical_job_id, version_number));
    """)


def downgrade() -> None:
    op.execute("""
    DROP TABLE manual_job_records;
    DROP TABLE job_deduplication_candidates;
    DROP TABLE job_source_links;
    ALTER TABLE raw_job_records DROP CONSTRAINT fk_raw_canonical_job;
    ALTER TABLE canonical_jobs DROP CONSTRAINT fk_canonical_current_version;
    DROP TABLE canonical_job_versions;
    DROP TABLE canonical_jobs;
    DROP TABLE raw_job_record_versions;
    DROP TABLE raw_job_records;
    DROP TABLE source_sync_runs;
    DROP TABLE ats_registry_entries;
    """)
