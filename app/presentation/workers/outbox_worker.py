import asyncio

from app.infrastructure.messaging.publisher import EventPublisher
from app.infrastructure.persistence.sqlalchemy.repositories import (
    get_unprocessed_events,
    mark_as_processed,
    mark_failed,
)


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
