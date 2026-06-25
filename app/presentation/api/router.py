from fastapi import APIRouter

from app.presentation.api.routes.payments import router as payments_router

router = APIRouter(prefix="/api/v1")
router.include_router(payments_router)
