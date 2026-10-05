"""Database models for SOS records and auditable alerts."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (Index("ix_alert_zone_created", "zone_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    zone_id: Mapped[str] = mapped_column(String(160), nullable=False)
    location: Mapped[str] = mapped_column(String(240), nullable=False)
    pincode: Mapped[str | None] = mapped_column(String(16))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="Created")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(4), nullable=False, default="en")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    audit_entries: Mapped[list[AlertAudit]] = relationship(
        back_populates="alert", cascade="all, delete-orphan", order_by="AlertAudit.sequence"
    )


class AlertAudit(Base):
    __tablename__ = "alert_audit"
    __table_args__ = (
        UniqueConstraint("alert_id", "sequence", name="uq_alert_audit_sequence"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    alert_id: Mapped[str] = mapped_column(ForeignKey("alerts.id"), nullable=False, index=True)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    event: Mapped[str] = mapped_column(String(40), nullable=False)
    actor: Mapped[str] = mapped_column(String(160), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    previous_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    entry_hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Mapped[str] = mapped_column(String(40), nullable=False)
    alert: Mapped[Alert] = relationship(back_populates="audit_entries")


class SosRequest(Base):
    __tablename__ = "sos_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    phone: Mapped[str] = mapped_column(String(40), nullable=False)
    pincode: Mapped[str | None] = mapped_column(String(16))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    message: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(24), nullable=False, default="Created")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
