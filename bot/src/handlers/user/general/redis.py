import json

from loguru import logger

from config.config_reader import settings
from src.database.connection_redis import r_async


@logger.catch()
async def set_general_button_callback(uuid_key, data):
    key = f"general:{uuid_key}:callback"
    val = json.dumps(data)
    await r_async.set(key, value=val, ex=settings.REDIS_RECORD_LIFETIME)


@logger.catch()
async def get_general_button_callback(uuid_key):
    key = f"general:{uuid_key}:callback"
    val = await r_async.get(key)
    if val:
        val = json.loads(val)
    return val
