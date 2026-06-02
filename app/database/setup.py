import os

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASS = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_NAME = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
async_engine: AsyncEngine = create_async_engine(DATABASE_URL)


async def check_db_connection() -> None:
    engine = create_async_engine(DATABASE_URL, echo=False)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except OperationalError as e:
        raise RuntimeError("Database is not available") from e
    finally:
        await engine.dispose()


# def run_migrations() -> None:
#     alembic_cfg = Config("alembic.ini")
#     os.environ["ALEMBIC_SKIP_MODEL_IMPORTS"] = "1"
#     command.upgrade(alembic_cfg, "head")
