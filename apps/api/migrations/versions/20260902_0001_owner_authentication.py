"""Add the single-owner authentication foundation.

Revision ID: 20260902_0001
Revises:
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260902_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "installation",
        sa.Column("id", sa.SmallInteger(), nullable=False),
        sa.Column("initialized_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("id = 1", name="ck_installation_singleton"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(sa.table("installation", sa.column("id", sa.SmallInteger())), [{"id": 1}])
    op.create_table(
        "owner_account",
        sa.Column("id", sa.SmallInteger(), nullable=False),
        sa.Column("password_verifier", sa.String(length=512), nullable=False),
        sa.Column("credential_version", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("password_changed_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_owner_account_singleton"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "login_rate_limits",
        sa.Column("rate_key", sa.String(length=32), nullable=False),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False),
        sa.Column("blocked_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("window_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("window_attempts", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("rate_key"),
    )
    op.create_table(
        "security_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metadata_json", sa.JSON(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_security_events_created_at", "security_events", ["created_at"])
    op.create_table(
        "sessions",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("owner_id", sa.SmallInteger(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_activity_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("idle_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("absolute_expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revocation_reason", sa.String(length=64), nullable=True),
        sa.Column("credential_version", sa.Integer(), nullable=False),
        sa.Column("client_label", sa.String(length=80), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["owner_account.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_sessions_active_activity", "sessions", ["revoked_at", "last_activity_at"])
    op.create_index("ix_sessions_token_hash", "sessions", ["token_hash"], unique=True)
    op.create_table(
        "session_csrf_tokens",
        sa.Column("session_id", sa.String(length=36), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("session_id"),
        sa.UniqueConstraint("token_hash"),
    )


def downgrade() -> None:
    op.drop_table("session_csrf_tokens")
    op.drop_index("ix_sessions_token_hash", table_name="sessions")
    op.drop_index("ix_sessions_active_activity", table_name="sessions")
    op.drop_table("sessions")
    op.drop_index("ix_security_events_created_at", table_name="security_events")
    op.drop_table("security_events")
    op.drop_table("login_rate_limits")
    op.drop_table("owner_account")
    op.drop_table("installation")
