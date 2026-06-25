import asyncio
import random
from datetime import datetime, timezone

from app.domain.payments.enums import Status
from app.infrastructure.messaging.broker import broker
from app.infrastructure.persistence.session import AsyncSessionLocal
from app.infrastructure.persistence.sqlalchemy.models import Payments, Outbox
from app.infrastructure.persistence.sqlalchemy.repositories import get_payment_by_id


@broker.subscriber("payment.created")
async def handle_payment_created(message: dict):
    async with AsyncSessionLocal() as session:
        async with session.begin():
            payment = await get_payment_by_id(session, message["payment_id"])

            if payment is None or payment.processed_at:
                return
            if payment.status in (Status.succeeded, Status.failed):
                return

            await simulate_processing()

            success = random.random() < 0.9

            payment.status = Status.succeeded if success else Status.failed
            payment.processed_at = datetime.now(timezone.utc)

            session.add(payment)

            event = build_webhook_event(payment)
            session.add(event)


def build_webhook_event(payment: Payments) -> Outbox:
    return Outbox(
        event_type=(
            "payment.succeeded"
            if payment.status == Status.succeeded
            else "payment.failed"
        ),
        payload={
            "payment_id": str(payment.payment_id),
            "status": payment.status.value,
            "amount": str(payment.amount),
            "currency": payment.currency.value,
        },
    )


async def simulate_processing():
    await asyncio.sleep(random.uniform(2, 5))
