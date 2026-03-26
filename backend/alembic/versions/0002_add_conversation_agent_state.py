"""Add agent state to conversations for tutor orchestration."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_agent_state"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column("agent_state", sa.JSON(), nullable=False, server_default=sa.text("'{}'::json")),
    )
    op.alter_column("conversations", "agent_state", server_default=None)


def downgrade() -> None:
    op.drop_column("conversations", "agent_state")
