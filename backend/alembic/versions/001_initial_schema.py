"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-04-07
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "coaches",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, index=True, nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "athletes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("coach_id", sa.String(36), sa.ForeignKey("coaches.id"), nullable=False),
        sa.Column("first_name", sa.String(255), nullable=False),
        sa.Column("last_name", sa.String(255), nullable=False),
        sa.Column(
            "handedness",
            sa.Enum("left", "right", name="handedness"),
            nullable=False,
            server_default="right",
        ),
        sa.Column(
            "primary_swing_type",
            sa.Enum(
                "regular", "left_slap", "power_slap", "drag", "bunt", name="swingtype"
            ),
            nullable=False,
            server_default="regular",
        ),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("athlete_id", sa.String(36), sa.ForeignKey("athletes.id"), nullable=False),
        sa.Column("coach_id", sa.String(36), sa.ForeignKey("coaches.id"), nullable=False),
        sa.Column("session_type", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "swings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("session_id", sa.String(36), sa.ForeignKey("sessions.id"), nullable=False),
        sa.Column(
            "swing_type",
            sa.Enum(
                "regular", "left_slap", "power_slap", "drag", "bunt", name="swingtype"
            ),
            nullable=False,
            server_default="regular",
        ),
        sa.Column("source_video_url", sa.String(500), nullable=False),
        sa.Column("processed_data_url", sa.String(500), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "uploaded", "queued", "processing", "review_ready", "failed",
                name="swingstatus",
            ),
            nullable=False,
            server_default="uploaded",
        ),
        sa.Column("pipeline_version", sa.String(50), nullable=False, server_default="0.1.0"),
        sa.Column("notes", sa.String(2000), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "event_reviews",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "swing_id", sa.String(36), sa.ForeignKey("swings.id"), unique=True, nullable=False
        ),
        sa.Column("auto_start_frame", sa.Integer, nullable=False),
        sa.Column("auto_launch_frame", sa.Integer, nullable=False),
        sa.Column("auto_contact_frame", sa.Integer, nullable=False),
        sa.Column("final_start_frame", sa.Integer, nullable=False),
        sa.Column("final_launch_frame", sa.Integer, nullable=False),
        sa.Column("final_contact_frame", sa.Integer, nullable=False),
        sa.Column("manual_override", sa.Boolean, server_default="false"),
        sa.Column("event_confidence", sa.Float, server_default="0.0"),
    )

    op.create_table(
        "metric_snapshots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "swing_id", sa.String(36), sa.ForeignKey("swings.id"), unique=True, nullable=False
        ),
        sa.Column("metrics_json", JSONB, nullable=False, server_default="{}"),
        sa.Column("deltas_json", JSONB, nullable=False, server_default="{}"),
        sa.Column("timing_json", JSONB, nullable=False, server_default="{}"),
        sa.Column("landmark_confidence", sa.Float, server_default="0.0"),
    )

    op.create_table(
        "interpretations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "swing_id", sa.String(36), sa.ForeignKey("swings.id"), unique=True, nullable=False
        ),
        sa.Column("what_happened", sa.Text, nullable=False),
        sa.Column("what_it_means", sa.Text, nullable=False),
        sa.Column("what_to_coach_next", sa.Text, nullable=False),
        sa.Column("rules_triggered", JSONB, nullable=False, server_default="[]"),
        sa.Column(
            "severity",
            sa.Enum("high", "medium", "low", name="severity"),
            nullable=False,
            server_default="low",
        ),
    )


def downgrade():
    op.drop_table("interpretations")
    op.drop_table("metric_snapshots")
    op.drop_table("event_reviews")
    op.drop_table("swings")
    op.drop_table("sessions")
    op.drop_table("athletes")
    op.drop_table("coaches")
    op.execute("DROP TYPE IF EXISTS severity")
    op.execute("DROP TYPE IF EXISTS swingstatus")
    op.execute("DROP TYPE IF EXISTS swingtype")
    op.execute("DROP TYPE IF EXISTS handedness")
