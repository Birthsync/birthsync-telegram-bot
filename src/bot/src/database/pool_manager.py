# db_pool_manager.py
import asyncpg
from loguru import logger

from config.config_reader import settings

db_pool = None


@logger.catch()
async def init_connection(conn):
    try:
        await conn.execute('SET statement_timeout = 5000')
        await conn.execute('SET lock_timeout = 5000')
        logger.debug(f"Timeouts установлены")
    except Exception as e:
        logger.error(f"Ошибка при установке таймаутов: {e}")
        raise


async def init_db_pool():
    global db_pool
    if db_pool is None:
        try:
            db_pool = await asyncpg.create_pool(
                user=settings.DB_USER,
                password=settings.DB_PASS.get_secret_value(),
                database=settings.DB_NAME,
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                min_size=1,
                max_size=100,
                init=init_connection,
            )
            logger.success("Database pool successfully created!")
        except Exception as e:
            logger.error(f"Failed to create database pool: {e}")
            raise


async def close_db_pool():
    global db_pool
    if db_pool is not None:
        await db_pool.close()
        logger.success("Database pool successfully closed!")
        db_pool = None


async def get_db_pool():
    if db_pool is None:
        await init_db_pool()
    return db_pool
