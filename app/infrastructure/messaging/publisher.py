from app.infrastructure.messaging.broker import broker
from app.infrastructure.persistence.sqlalchemy.models import Outbox


class EventPublisher:
    async def publish(self, event: Outbox):
        await broker.publish(
            message=event.payload,
            routing_key=event.event_type,
            headers={"event_id": str(event.id)},
        )
