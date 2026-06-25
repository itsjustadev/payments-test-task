from pydantic import BaseModel, Json
from uuid import UUID
from decimal import Decimal
from typing import Any
from datetime import datetime

from app.domain.payments.enums import Currency, Status


class Payment(BaseModel):
    payment_id: UUID
    amount: Decimal
    currency: Currency
    description: str
    metadata: Json[Any]
    status: Status
    idempotency_key: UUID
    webhook_url: str
    created_at: datetime
    processed_at: datetime
