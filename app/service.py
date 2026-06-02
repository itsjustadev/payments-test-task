from fastapi import Header, HTTPException, status
from app.constants import API_KEY
from app.database.core import create_payment_workflow
from app.database.models import Payments
from app.entities import CreatePaymentCommand, Status
from app.database.core import get_payment_by_id

from datetime import datetime, timezone
from uuid import uuid4


async def verify_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
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
