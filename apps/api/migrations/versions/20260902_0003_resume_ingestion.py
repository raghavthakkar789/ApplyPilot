"""Add protected resume ingestion and deterministic extraction records.

Revision ID: 20260902_0003
Revises: 20260902_0002
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260902_0003"
down_revision: str | None = "20260902_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "stored_documents",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("storage_key", sa.String(100), nullable=False, unique=True),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("byte_length", sa.BigInteger(), nullable=False),
        sa.Column("detected_media_type", sa.String(100), nullable=False),
        sa.Column("document_format", sa.String(12), nullable=False),
        sa.Column("integrity_state", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint("byte_length >= 0", name="ck_stored_document_size"),
        sa.UniqueConstraint("sha256", "byte_length", name="uq_stored_document_content"),
    )
    op.create_table(
        "resumes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("owner_id", sa.SmallInteger(), nullable=False),
        sa.Column("display_name", sa.String(160), nullable=False),
        sa.Column("purpose", sa.String(160)),
        sa.Column("current_version_id", sa.String(36)),
        sa.Column("archived", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("trashed_at", sa.DateTime(timezone=True)),
        sa.Column("purge_after", sa.DateTime(timezone=True)),
        sa.ForeignKeyConstraint(["owner_id"], ["owner_account.id"], ondelete="RESTRICT"),
    )
    op.create_index("ix_resumes_owner_trash", "resumes", ["owner_id", "trashed_at"])
    op.create_table(
        "resume_versions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("resume_id", sa.String(36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.String(36), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("declared_media_type", sa.String(100), nullable=False),
        sa.Column("parser_name", sa.String(50), nullable=False),
        sa.Column("parser_version", sa.String(50), nullable=False),
        sa.Column("extraction_status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("superseded_at", sa.DateTime(timezone=True)),
        sa.Column("trashed_at", sa.DateTime(timezone=True)),
        sa.Column("permanently_deleted_at", sa.DateTime(timezone=True)),
        sa.CheckConstraint(
            "extraction_status IN ('pending','succeeded','failed')",
            name="ck_resume_extraction_status",
        ),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["document_id"], ["stored_documents.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("resume_id", "version_number", name="uq_resume_version_number"),
    )
    op.create_index(
        "ix_resume_versions_resume_created", "resume_versions", ["resume_id", "created_at"]
    )
    op.create_foreign_key(
        "fk_resumes_current_version", "resumes", "resume_versions", ["current_version_id"], ["id"]
    )
    op.create_table(
        "document_extractions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("resume_version_id", sa.String(36), nullable=False, unique=True),
        sa.Column("extracted_text", sa.Text()),
        sa.Column("page_count", sa.Integer()),
        sa.Column("paragraph_count", sa.Integer()),
        sa.Column("segments", sa.JSON(), nullable=False),
        sa.Column("warnings", sa.JSON(), nullable=False),
        sa.Column("parser_result", sa.String(20), nullable=False),
        sa.Column("extracted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("integrity_hash", sa.String(64)),
        sa.Column("failure_category", sa.String(60)),
        sa.ForeignKeyConstraint(["resume_version_id"], ["resume_versions.id"], ondelete="RESTRICT"),
    )
    op.create_table(
        "resume_fact_candidates",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("resume_version_id", sa.String(36), nullable=False),
        sa.Column("fact_type", sa.String(64), nullable=False),
        sa.Column("semantic_key", sa.String(160), nullable=False),
        sa.Column("proposed_value", sa.JSON(), nullable=False),
        sa.Column("evidence_citation", sa.String(500), nullable=False),
        sa.Column("extraction_method", sa.String(80), nullable=False),
        sa.Column("confidence", sa.String(16)),
        sa.Column("review_status", sa.String(16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True)),
        sa.Column("resulting_fact_identity_id", sa.String(36)),
        sa.Column("resulting_fact_version_id", sa.String(36)),
        sa.CheckConstraint(
            "review_status IN ('pending','accepted','rejected')",
            name="ck_resume_candidate_review_status",
        ),
        sa.ForeignKeyConstraint(["resume_version_id"], ["resume_versions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["resulting_fact_identity_id"], ["candidate_fact_identities.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["resulting_fact_version_id"], ["candidate_fact_versions.id"], ondelete="RESTRICT"
        ),
    )
    op.create_index(
        "ix_resume_candidates_version_status",
        "resume_fact_candidates",
        ["resume_version_id", "review_status"],
    )
    op.create_table(
        "document_lifecycle_events",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("resume_id", sa.String(36)),
        sa.Column("resume_version_id", sa.String(36)),
        sa.Column("event_type", sa.String(50), nullable=False),
        sa.Column("outcome", sa.String(20), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["resume_id"], ["resumes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["resume_version_id"], ["resume_versions.id"], ondelete="RESTRICT"),
    )
    op.execute(
        """
        CREATE FUNCTION prevent_resume_version_update() RETURNS trigger AS $$
        BEGIN
          IF NEW.resume_id IS DISTINCT FROM OLD.resume_id
             OR NEW.version_number IS DISTINCT FROM OLD.version_number
             OR NEW.document_id IS DISTINCT FROM OLD.document_id
             OR NEW.original_filename IS DISTINCT FROM OLD.original_filename
             OR NEW.declared_media_type IS DISTINCT FROM OLD.declared_media_type
             OR NEW.parser_name IS DISTINCT FROM OLD.parser_name
             OR NEW.parser_version IS DISTINCT FROM OLD.parser_version
             OR NEW.created_at IS DISTINCT FROM OLD.created_at THEN
            RAISE EXCEPTION 'resume version content is immutable';
          END IF;
          RETURN NEW;
        END; $$ LANGUAGE plpgsql;
        CREATE TRIGGER resume_version_immutable
          BEFORE UPDATE ON resume_versions
          FOR EACH ROW EXECUTE FUNCTION prevent_resume_version_update();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER resume_version_immutable ON resume_versions")
    op.execute("DROP FUNCTION prevent_resume_version_update")
    op.drop_table("document_lifecycle_events")
    op.drop_index("ix_resume_candidates_version_status", table_name="resume_fact_candidates")
    op.drop_table("resume_fact_candidates")
    op.drop_table("document_extractions")
    op.drop_constraint("fk_resumes_current_version", "resumes", type_="foreignkey")
    op.drop_index("ix_resume_versions_resume_created", table_name="resume_versions")
    op.drop_table("resume_versions")
    op.drop_index("ix_resumes_owner_trash", table_name="resumes")
    op.drop_table("resumes")
    op.drop_table("stored_documents")
