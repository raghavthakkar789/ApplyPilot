"""Add candidate profiles and immutable verified facts.

Revision ID: 20260902_0002
Revises: 20260902_0001
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260902_0002"
down_revision: str | None = "20260902_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "candidate_profiles",
        sa.Column("owner_id", sa.SmallInteger(), nullable=False),
        sa.Column("sections", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("owner_id = 1", name="ck_candidate_profile_singleton"),
        sa.ForeignKeyConstraint(["owner_id"], ["owner_account.id"]),
        sa.PrimaryKeyConstraint("owner_id"),
    )
    op.create_table(
        "candidate_fact_identities",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("owner_id", sa.SmallInteger(), nullable=False),
        sa.Column("fact_type", sa.String(64), nullable=False),
        sa.Column("semantic_key", sa.String(160), nullable=False),
        sa.Column("scope", sa.String(160), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["owner_account.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "semantic_key", "scope", name="uq_fact_identity_key_scope"),
    )
    op.create_index(
        "ix_fact_identity_semantic_scope", "candidate_fact_identities", ["semantic_key", "scope"]
    )
    op.create_table(
        "candidate_fact_versions",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("fact_identity_id", sa.String(36), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("typed_value", sa.JSON(), nullable=False),
        sa.Column("lifecycle_state", sa.String(16), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("source_reference", sa.String(240)),
        sa.Column("source_version", sa.String(120)),
        sa.Column("evidence_citation", sa.String(500)),
        sa.Column("extraction_method", sa.String(80)),
        sa.Column("extraction_confidence", sa.String(16)),
        sa.Column("owner_confirmed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("superseded_at", sa.DateTime(timezone=True)),
        sa.Column("supersession_reason", sa.String(240)),
        sa.Column("revoked_at", sa.DateTime(timezone=True)),
        sa.Column("revocation_reason", sa.String(240)),
        sa.Column("sensitivity", sa.String(32), nullable=False),
        sa.Column("reconfirmation_policy", sa.String(40), nullable=False),
        sa.Column("reconfirmation_due_at", sa.DateTime(timezone=True)),
        sa.Column("integrity_hash", sa.String(64), nullable=False),
        sa.CheckConstraint(
            "lifecycle_state IN ('unverified','verified','stale','conflicted','revoked')",
            name="ck_fact_version_state",
        ),
        sa.ForeignKeyConstraint(["fact_identity_id"], ["candidate_fact_identities.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fact_identity_id", "version_number", name="uq_fact_version_number"),
    )
    op.create_index(
        "ix_fact_version_current",
        "candidate_fact_versions",
        ["fact_identity_id", "superseded_at", "lifecycle_state"],
    )
    op.create_index(
        "ix_fact_version_reconfirmation",
        "candidate_fact_versions",
        ["reconfirmation_due_at", "lifecycle_state"],
    )
    op.execute(
        """
        CREATE FUNCTION prevent_candidate_fact_value_update() RETURNS trigger AS $$
        BEGIN
          IF NEW.typed_value::jsonb IS DISTINCT FROM OLD.typed_value::jsonb
             OR NEW.fact_identity_id IS DISTINCT FROM OLD.fact_identity_id
             OR NEW.version_number IS DISTINCT FROM OLD.version_number
             OR NEW.integrity_hash IS DISTINCT FROM OLD.integrity_hash THEN
            RAISE EXCEPTION 'candidate fact version values are immutable';
          END IF;
          RETURN NEW;
        END; $$ LANGUAGE plpgsql;
        CREATE TRIGGER candidate_fact_value_immutable
          BEFORE UPDATE ON candidate_fact_versions
          FOR EACH ROW EXECUTE FUNCTION prevent_candidate_fact_value_update();
        """
    )
    op.create_table(
        "candidate_fact_confirmations",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("fact_version_id", sa.String(36), nullable=False),
        sa.Column("confirmation_type", sa.String(24), nullable=False),
        sa.Column("confirmed_by_owner_id", sa.SmallInteger(), nullable=False),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["fact_version_id"], ["candidate_fact_versions.id"]),
        sa.ForeignKeyConstraint(["confirmed_by_owner_id"], ["owner_account.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "candidate_fact_lifecycle_events",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("fact_version_id", sa.String(36), nullable=False),
        sa.Column("event_type", sa.String(40), nullable=False),
        sa.Column("reason", sa.String(240)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["fact_version_id"], ["candidate_fact_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "candidate_fact_evidence",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("fact_version_id", sa.String(36), nullable=False),
        sa.Column("source_type", sa.String(32), nullable=False),
        sa.Column("source_identifier", sa.String(240)),
        sa.Column("source_version", sa.String(120)),
        sa.Column("citation", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["fact_version_id"], ["candidate_fact_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "candidate_fact_conflicts",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("semantic_key", sa.String(160), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True)),
        sa.Column("resolution_reason", sa.String(240)),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "candidate_fact_conflict_members",
        sa.Column("conflict_id", sa.String(36), nullable=False),
        sa.Column("fact_version_id", sa.String(36), nullable=False),
        sa.ForeignKeyConstraint(["conflict_id"], ["candidate_fact_conflicts.id"]),
        sa.ForeignKeyConstraint(["fact_version_id"], ["candidate_fact_versions.id"]),
        sa.PrimaryKeyConstraint("conflict_id", "fact_version_id"),
    )


def downgrade() -> None:
    op.drop_table("candidate_fact_conflict_members")
    op.drop_table("candidate_fact_conflicts")
    op.drop_table("candidate_fact_evidence")
    op.drop_table("candidate_fact_lifecycle_events")
    op.drop_table("candidate_fact_confirmations")
    op.execute("DROP TRIGGER candidate_fact_value_immutable ON candidate_fact_versions")
    op.execute("DROP FUNCTION prevent_candidate_fact_value_update")
    op.drop_index("ix_fact_version_reconfirmation", table_name="candidate_fact_versions")
    op.drop_index("ix_fact_version_current", table_name="candidate_fact_versions")
    op.drop_table("candidate_fact_versions")
    op.drop_index("ix_fact_identity_semantic_scope", table_name="candidate_fact_identities")
    op.drop_table("candidate_fact_identities")
    op.drop_table("candidate_profiles")
