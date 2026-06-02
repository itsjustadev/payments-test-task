print("🔥 FILE EXECUTED")
import asyncio
from app.database.core import AsyncSessionLocal
from app.workers.outbox_worker import outbox_worker
from app.workers.outbox_worker import webhook_worker
from app.messaging.publisher import EventPublisher
from app.messaging.broker import broker


async def main():

    publisher = EventPublisher()
    await broker.connect()

    await asyncio.gather(
        outbox_worker(AsyncSessionLocal, publisher),
        webhook_worker(AsyncSessionLocal),
    )


if __name__ == "__main__":
    asyncio.run(main())
