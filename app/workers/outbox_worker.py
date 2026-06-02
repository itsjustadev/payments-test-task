from app.database.core import (
    get_unprocessed_events,
    mark_as_processed,
    mark_failed,
    get_payment_by_id,
    get_webhook_events,
)
import asyncio
from app.database.models import Outbox
from datetime import datetime, timedelta, timezone
import httpx
from app.messaging.publisher import EventPublisher

publisher = EventPublisher()


async def outbox_worker(session_factory, publisher: EventPublisher):
    print("outbox worker started")
    while True:
        async with session_factory() as session:
            async with session.begin():
                events = await get_unprocessed_events(session)
                print(events)

        print(f"📦 EVENTS COUNT: {len(events)}")

        for event in events:
            try:
                print("📤 BEFORE PUBLISH")
                await publisher.publish(event)
                print("📤 AFTER PUBLISH")

                async with session_factory() as session:
                    async with session.begin():
                        await mark_as_processed(session, event)

            except Exception as e:
                async with session_factory() as session:
                    async with session.begin():
                        await mark_failed(session, event, str(e))

        await asyncio.sleep(1)


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


async def send_webhook(client, url: str, payload: dict) -> bool:
    try:
        response = await client.post(url, json=payload)
        return 200 <= response.status_code < 300
    except Exception:
        return False
