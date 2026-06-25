import asyncio

from app.infrastructure.messaging.broker import broker
from app.infrastructure.messaging.publisher import EventPublisher
from app.infrastructure.persistence.session import AsyncSessionLocal
from app.presentation.workers.outbox_worker import outbox_worker
from app.presentation.workers.webhook_worker import webhook_worker


async def main():
    publisher = EventPublisher()
    await broker.connect()

    await asyncio.gather(
        outbox_worker(AsyncSessionLocal, publisher),
        webhook_worker(AsyncSessionLocal),
    )


if __name__ == "__main__":
    asyncio.run(main())
