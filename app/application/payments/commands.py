from decimal import Decimal

from pydantic import BaseModel


class CreatePaymentCommand(BaseModel):
    amount: Decimal
    currency: str
    description: str
    meta_data: dict
    webhook_url: str
    idempotency_key: str
