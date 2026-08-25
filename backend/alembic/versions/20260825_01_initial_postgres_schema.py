"""Create PostgreSQL schema for application state.

Revision ID: 20260825_01
Revises:
Create Date: 2026-08-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260825_01"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("username", sa.String(50), nullable=False, unique=True),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("full_name", sa.String(255)),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_workspace_id", "users", ["workspace_id"])
    op.create_table(
        "workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("sentry_api_token", sa.Text()), sa.Column("sentry_organization", sa.String(255)),
        sa.Column("sentry_test_dsn", sa.Text()), sa.Column("openai_api_key", sa.Text()),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_workspaces_name", "workspaces", ["name"])
    op.create_index("ix_workspaces_owner_id", "workspaces", ["owner_id"])
    op.create_table(
        "workspace_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False, unique=True),
        sa.Column("openai_model", sa.String(100), nullable=False), sa.Column("auto_analyze", sa.Boolean(), nullable=False),
        sa.Column("notification_email", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "processed_issues",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("sentry_issue_id", sa.String(255), nullable=False), sa.Column("sentry_issue", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("ai_analysis", postgresql.JSONB(astext_type=sa.Text())), sa.Column("status", sa.String(32), nullable=False),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True)), sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspaces.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("sentry_issue_id", "workspace_id", name="uq_processed_issue_workspace"),
    )
    op.create_index("ix_processed_issues_sentry_issue_id", "processed_issues", ["sentry_issue_id"])
    op.create_index("ix_processed_issues_workspace_id", "processed_issues", ["workspace_id"])
    op.create_index("ix_processed_issues_workspace_created", "processed_issues", ["workspace_id", "created_at"])
    op.create_index("ix_processed_issues_workspace_status", "processed_issues", ["workspace_id", "status"])


def downgrade() -> None:
    op.drop_table("processed_issues")
    op.drop_table("workspace_settings")
    op.drop_table("workspaces")
    op.drop_table("users")
