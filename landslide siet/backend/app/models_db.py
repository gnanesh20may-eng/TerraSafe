from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class SosRecord(Base):
    __tablename__ = "sos_reports"
    __table_args__ = (Index("ix_sos_created_status", "created_at", "status"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    message: Mapped[str] = mapped_column(String(500), default="Emergency assistance requested")
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="OPEN", nullable=False)
    source: Mapped[str] = mapped_column(String(24), default="WEB", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)


class AlertRecord(Base):
    __tablename__ = "alerts"
    __table_args__ = (
        Index("ix_alert_location_created", "location_id", "created_at"),
        Index("ix_alert_state_created", "lifecycle_state", "created_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    location_id: Mapped[str] = mapped_column(String(100), nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    lifecycle_state: Mapped[str] = mapped_column(String(24), default="CREATED", nullable=False)
    created_by: Mapped[str] = mapped_column(String(100), default="system", nullable=False)
    approved_by: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    events: Mapped[list["AlertEventRecord"]] = relationship(back_populates="alert", cascade="all, delete-orphan", order_by="AlertEventRecord.sequence")


class AlertEventRecord(Base):
    __tablename__ = "alert_events"
    __table_args__ = (
        UniqueConstraint("alert_id", "sequence", name="uq_alert_event_sequence"),
        Index("ix_alert_events_alert_sequence", "alert_id", "sequence"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    alert_id: Mapped[str] = mapped_column(ForeignKey("alerts.id", ondelete="CASCADE"), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    from_state: Mapped[str | None] = mapped_column(String(24), nullable=True)
    to_state: Mapped[str] = mapped_column(String(24), nullable=False)
    actor: Mapped[str] = mapped_column(String(100), nullable=False)
    detail: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    event_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    alert: Mapped[AlertRecord] = relationship(back_populates="events")
