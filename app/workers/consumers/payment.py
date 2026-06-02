from datetime import datetime, timezone
import random
import asyncio

from app.messaging.broker import broker
from app.database.core import AsyncSessionLocal, get_payment_by_id
from app.database.models import Status, Payments, Outbox


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
