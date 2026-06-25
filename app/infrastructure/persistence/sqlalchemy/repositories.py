import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.persistence.sqlalchemy.models import Base, Payments, Outbox

logger = logging.getLogger("app.infrastructure.persistence")


async def create_all_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created successfully")


async def insert_payment(session: AsyncSession, payment: Payments) -> Payments | None:
    stmt = (
        insert(Payments)
        .values(
            payment_id=payment.payment_id,
            amount=payment.amount,
            currency=payment.currency,
            description=payment.description,
            meta_data=payment.meta_data,
            status=payment.status,
            idempotency_key=payment.idempotency_key,
            webhook_url=payment.webhook_url,
            created_at=payment.created_at,
        )
        .on_conflict_do_nothing(index_elements=["idempotency_key"])
        .returning(Payments)
    )

    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_payment_by_key(session: AsyncSession, key: UUID) -> Payments | None:
    result = await session.execute(
        select(Payments).where(Payments.idempotency_key == key)
    )
    return result.scalar_one_or_none()


def build_payment_created_event(payment: Payments) -> Outbox:
    return Outbox(
        event_type="payment.created",
        payload={
            "payment_id": str(payment.payment_id),
            "amount": str(payment.amount),
            "currency": payment.currency,
            "status": payment.status.value,
        },
    )


async def create_payment_workflow(
    session: AsyncSession,
    payment: Payments,
) -> Payments:
    inserted = await insert_payment(session, payment)

    if inserted:
        event = build_payment_created_event(inserted)
        session.add(event)
        return inserted

    existing = await get_payment_by_key(
        session,
        payment.idempotency_key,
    )
    if existing is None:
        raise RuntimeError("Payment not found after conflict")

    return existing


async def get_unprocessed_events(session: AsyncSession, limit: int = 100):
    result = await session.execute(
        select(Outbox)
        .where(Outbox.processed_at.is_(None))
        .where(Outbox.attempts < 3)
        .limit(limit)
    )

    return result.scalars().all()


async def mark_as_processed(session: AsyncSession, event: Outbox):
    event.processed_at = datetime.now(timezone.utc)


async def mark_failed(session: AsyncSession, event: Outbox, error: str):
    event.attempts += 1
    event.last_error = error


async def get_payment_by_id(
    session: AsyncSession,
    payment_id: UUID,
) -> Payments | None:
    result = await session.execute(
        select(Payments).where(Payments.payment_id == payment_id)
    )

    return result.scalar_one_or_none()


async def get_webhook_events(session):
    result = await session.execute(
        select(Outbox)
        .where(Outbox.processed_at.is_(None))
        .where(Outbox.attempts < 3)
        .where(Outbox.dead_at.is_(None))
        .where(
            (Outbox.next_retry_at.is_(None))
            | (Outbox.next_retry_at <= datetime.now(timezone.utc))
        )
        .where(Outbox.event_type.in_(["payment.succeeded", "payment.failed"]))
        .with_for_update(skip_locked=True)
    )

    return result.scalars().all()
