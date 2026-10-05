"""Create alert, hash-chain audit, and SOS tables."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "0001_alerts_and_sos"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "alerts",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("zone_id", sa.String(length=160), nullable=False),
        sa.Column("location", sa.String(length=240), nullable=False),
        sa.Column("pincode", sa.String(length=16)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("risk_score", sa.Float(), nullable=False),
        sa.Column("risk_level", sa.String(length=16), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("language", sa.String(length=4), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_alert_zone_created", "alerts", ["zone_id", "created_at"])
    op.create_table(
        "alert_audit",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("alert_id", sa.String(length=36), sa.ForeignKey("alerts.id"), nullable=False),
        sa.Column("sequence", sa.Integer(), nullable=False),
        sa.Column("event", sa.String(length=40), nullable=False),
        sa.Column("actor", sa.String(length=160), nullable=False),
        sa.Column("payload", sa.Text(), nullable=False),
        sa.Column("previous_hash", sa.String(length=64), nullable=False),
        sa.Column("entry_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.UniqueConstraint("alert_id", "sequence", name="uq_alert_audit_sequence"),
    )
    op.create_index("ix_alert_audit_alert_id", "alert_audit", ["alert_id"])
    op.create_table(
        "sos_requests",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("phone", sa.String(length=40), nullable=False),
        sa.Column("pincode", sa.String(length=16)),
        sa.Column("latitude", sa.Float()),
        sa.Column("longitude", sa.Float()),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("sos_requests")
    op.drop_index("ix_alert_audit_alert_id", table_name="alert_audit")
    op.drop_table("alert_audit")
    op.drop_index("ix_alert_zone_created", table_name="alerts")
    op.drop_table("alerts")
