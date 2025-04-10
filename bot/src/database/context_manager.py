# cont_manager_func.py

from contextlib import asynccontextmanager

from loguru import logger

from src.database.pool_manager import get_db_pool


@asynccontextmanager
async def db_connection():
    try:
        db_pool = await get_db_pool()
        async with db_pool.acquire() as conn:
            yield conn
    except Exception as e:
        logger.exception(f"Error acquiring connection: {e}")
        raise


@asynccontextmanager
async def db_cursor():
    try:
        async with db_connection() as conn:
            async with conn.transaction():
                yield conn
    except Exception as e:
        logger.exception(f"Error during transaction: {e}")
        raise

