from fastapi import FastAPI

from fastapi import FastAPI, APIRouter, status, Header, Depends, HTTPException
from app.entities import (
    CreatePaymentRequest,
    CreatePaymentResponse,
    CreatePaymentRequest,
    CreatePaymentCommand,
    PaymentResponse,
)
from app.service import verify_api_key, payment_workflow
from uuid import UUID
from app.database.core import AsyncSession
from app.database.deps import get_session
from app.service import PaymentService
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

payments_router = APIRouter(
    prefix="/api/v1/payments", dependencies=[Depends(verify_api_key)]
)


@payments_router.post(
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


@payments_router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: UUID, session: AsyncSession = Depends(get_session)):
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


app.include_router(payments_router)
