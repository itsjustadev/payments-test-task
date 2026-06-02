from pydantic import BaseModel, Json, Field
from uuid import UUID
from decimal import Decimal
from enum import Enum
from typing import Any
from datetime import datetime
from app.database.enums import Currency, Status


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


class CreatePaymentCommand(BaseModel):
    amount: Decimal
    currency: str
    description: str
    meta_data: dict
    webhook_url: str
    idempotency_key: str


class PaymentResponse(BaseModel):
    payment_id: UUID
    status: str
    amount: str
    currency: str
    processed_at: datetime | None
