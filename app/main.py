from fastapi import FastAPI
from dotenv import load_dotenv
from app.api import router as api_router

load_dotenv()

app = FastAPI(
    title="Payment API",
    version="1.0.0",
    description="API for processing payments",
)

app.include_router(api_router)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
