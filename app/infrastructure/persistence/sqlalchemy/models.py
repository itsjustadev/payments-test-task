from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime, timezone

from sqlalchemy import Enum, Numeric, DateTime, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, declarative_base

from app.domain.payments.enums import Status, Currency

Base = declarative_base()


class Payments(Base):
    __tablename__ = "payments"

    payment_id: Mapped[UUID] = mapped_column(
        PG_UUID,
        primary_key=True,
        default=uuid4,
    )

    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    currency: Mapped[Currency] = mapped_column(Enum(Currency), nullable=False)

    description: Mapped[str] = mapped_column(String, nullable=False)

    meta_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    status: Mapped[Status] = mapped_column(Enum(Status), nullable=False)

    idempotency_key: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        unique=True,
        index=True,
        nullable=False,
    )

    webhook_url: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class Outbox(Base):
    __tablename__ = "outbox"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid4
    )

    event_type: Mapped[str] = mapped_column(String, nullable=False)

    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)

    attempts: Mapped[int] = mapped_column(default=0, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_error: Mapped[str] = mapped_column(String, nullable=True)
    dead_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    next_retry_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
