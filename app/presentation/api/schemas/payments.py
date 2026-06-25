from decimal import Decimal
from typing import Any
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field


class CreatePaymentRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    description: str
    meta_data: dict[str, Any] = Field(default_factory=dict)
    webhook_url: str


class CreatePaymentResponse(BaseModel):
    payment_id: UUID
    status: str
    created_at: datetime


class PaymentResponse(BaseModel):
    payment_id: UUID
    status: str
    amount: str
    currency: str
    processed_at: datetime | None
