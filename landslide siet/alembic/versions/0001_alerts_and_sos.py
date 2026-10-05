"""Create alert lifecycle and SOS persistence tables."""

from alembic import op
import sqlalchemy as sa

revision = "0001_alerts_sos"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sos_reports",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("message", sa.String(length=500), nullable=False),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("source", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_sos_created_status", "sos_reports", ["created_at", "status"])
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("location_id", sa.String(length=100), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("message", sa.String(length=1000), nullable=False),
        sa.Column("lifecycle_state", sa.String(length=24), nullable=False),
        sa.Column("created_by", sa.String(length=100), nullable=False),
        sa.Column("approved_by", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_alert_location_created", "alerts", ["location_id", "created_at"])
    op.create_index("ix_alert_state_created", "alerts", ["lifecycle_state", "created_at"])
    op.create_table(
        "alert_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("alert_id", sa.String(length=36), sa.ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("from_state", sa.String(length=24), nullable=True),
        sa.Column("to_state", sa.String(length=24), nullable=False),
        sa.Column("actor", sa.String(length=100), nullable=False),
        sa.Column("detail", sa.String(length=500), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("previous_hash", sa.String(length=64), nullable=False),
        sa.Column("event_hash", sa.String(length=64), nullable=False),
        sa.UniqueConstraint("alert_id", "sequence", name="uq_alert_event_sequence"),
    )
    op.create_index("ix_alert_events_alert_sequence", "alert_events", ["alert_id", "sequence"])


def downgrade() -> None:
    op.drop_index("ix_alert_events_alert_sequence", table_name="alert_events")
    op.drop_table("alert_events")
    op.drop_index("ix_alert_state_created", table_name="alerts")
    op.drop_index("ix_alert_location_created", table_name="alerts")
    op.drop_table("alerts")
    op.drop_index("ix_sos_created_status", table_name="sos_reports")
    op.drop_table("sos_reports")
