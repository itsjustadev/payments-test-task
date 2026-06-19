from fastapi import APIRouter
from app.payments.payments import router as payments_router

router = APIRouter(prefix="/api/v1")
router.include_router(payments_router)
