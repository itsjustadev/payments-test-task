import asyncio
from datetime import datetime, timedelta, timezone

import httpx

from app.infrastructure.http.webhook_client import send_webhook
from app.infrastructure.persistence.sqlalchemy.models import Outbox
from app.infrastructure.persistence.sqlalchemy.repositories import (
    get_payment_by_id,
    get_webhook_events,
)


async def webhook_worker(session_factory):
    print("webhook worker started")
    async with httpx.AsyncClient(timeout=25) as client:
        while True:
            await process_webhook(session_factory, client)
            await asyncio.sleep(1)


async def process_webhook(session_factory, client):
    async with session_factory() as session:
        async with session.begin():
            events = await get_webhook_events(session)
            for event in events:
                payload = build_webhook_payload(event)
                payment = await get_payment_by_id(session, event.payload["payment_id"])
                if payment is None:
                    raise ValueError(
                        f"Payment not found: {event.payload['payment_id']}"
                    )
                url = payment.webhook_url
                success = await send_webhook(
                    client,
                    url,
                    payload,
                )

                if success:
                    event.processed_at = datetime.now(timezone.utc)
                else:
                    event.attempts += 1
                    event.last_error = "webhook failed"

                    if event.attempts >= 3:
                        event.dead_at = datetime.now(timezone.utc)
                    else:
                        delay = calculate_backoff(event.attempts)
                        event.next_retry_at = datetime.now(timezone.utc) + timedelta(
                            seconds=delay
                        )


def calculate_backoff(attempts: int, max_delay: int = 60) -> int:
    delay = 2**attempts
    return min(delay, max_delay)


def build_webhook_payload(event: Outbox) -> dict:
    return {
        "payment_id": event.payload["payment_id"],
        "status": event.payload["status"],
        "amount": event.payload["amount"],
        "currency": event.payload["currency"],
    }
