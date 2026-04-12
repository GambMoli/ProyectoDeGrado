"""Add topic metric events for report analytics."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_topic_metrics"
down_revision = "0003_auth_roles"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "topic_metric_events",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("conversation_id", sa.String(length=36), nullable=False),
        sa.Column("topic", sa.String(length=50), nullable=False),
        sa.Column("interaction_type", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_topic_metric_events_user_id"), "topic_metric_events", ["user_id"], unique=False)
    op.create_index(
        op.f("ix_topic_metric_events_conversation_id"),
        "topic_metric_events",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(op.f("ix_topic_metric_events_topic"), "topic_metric_events", ["topic"], unique=False)
    op.create_index(
        op.f("ix_topic_metric_events_interaction_type"),
        "topic_metric_events",
        ["interaction_type"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_topic_metric_events_interaction_type"), table_name="topic_metric_events")
    op.drop_index(op.f("ix_topic_metric_events_topic"), table_name="topic_metric_events")
    op.drop_index(op.f("ix_topic_metric_events_conversation_id"), table_name="topic_metric_events")
    op.drop_index(op.f("ix_topic_metric_events_user_id"), table_name="topic_metric_events")
    op.drop_table("topic_metric_events")
