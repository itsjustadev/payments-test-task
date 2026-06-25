from uuid import UUID

from fastapi import APIRouter, status, Header, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.payments.commands import CreatePaymentCommand
from app.application.payments.services.payment_service import PaymentService
from app.presentation.api.dependencies.auth import verify_api_key
from app.presentation.api.dependencies.session import get_session
from app.presentation.api.schemas.payments import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    PaymentResponse,
)

router = APIRouter(
    prefix="/api/v1/payments", dependencies=[Depends(verify_api_key)]
)


@router.post(
    "", response_model=CreatePaymentResponse, status_code=status.HTTP_202_ACCEPTED
)
async def create_payment(
    request: CreatePaymentRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_session),
) -> CreatePaymentResponse:
    cmd = CreatePaymentCommand(
        amount=request.amount,
        currency=request.currency,
        description=request.description,
        meta_data=request.meta_data,
        webhook_url=request.webhook_url,
        idempotency_key=idempotency_key,
    )
    payment = await PaymentService.create_payment(session, cmd)
    return CreatePaymentResponse(
        payment_id=payment.payment_id,
        status=payment.status.value,
        created_at=payment.created_at,
    )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID, session: AsyncSession = Depends(get_session)
):
    payment = await PaymentService.get_payment(session, payment_id)

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return PaymentResponse(
        payment_id=payment.payment_id,
        status=payment.status.value,
        amount=str(payment.amount),
        currency=payment.currency.value,
        processed_at=payment.processed_at,
    )
