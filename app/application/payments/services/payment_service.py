from datetime import datetime, timezone
from uuid import uuid4

from app.application.payments.commands import CreatePaymentCommand
from app.domain.payments.enums import Status
from app.infrastructure.persistence.sqlalchemy.models import Payments
from app.infrastructure.persistence.sqlalchemy.repositories import (
    create_payment_workflow,
    get_payment_by_id,
)


def build_payment(cmd: CreatePaymentCommand) -> Payments:
    return Payments(
        payment_id=uuid4(),
        amount=cmd.amount,
        currency=cmd.currency,
        description=cmd.description,
        meta_data=cmd.meta_data,
        status=Status.pending,
        idempotency_key=cmd.idempotency_key,
        webhook_url=cmd.webhook_url,
        created_at=datetime.now(timezone.utc),
    )


async def payment_workflow(session, cmd: CreatePaymentCommand) -> Payments:
    payment = build_payment(cmd)
    result: Payments | None = await create_payment_workflow(session, payment)
    return result


class PaymentService:

    @staticmethod
    async def create_payment(session, cmd):
        return await payment_workflow(session, cmd)

    @staticmethod
    async def get_payment(session, payment_id):
        return await get_payment_by_id(session, payment_id)
