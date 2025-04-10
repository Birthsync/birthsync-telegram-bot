import json

from loguru import logger

from config.config_reader import settings
from src.database.connection_redis import r_async


@logger.catch()
async def set_contacts_button_callback(uuid_key, data):
    key = f"general:{uuid_key}:callback"
    val = json.dumps(data)
    await r_async.set(key, value=val, ex=settings.REDIS_RECORD_LIFETIME)


@logger.catch()
async def get_contacts_button_callback(uuid_key):
    key = f"general:{uuid_key}:callback"
    val = await r_async.get(key)
    if val:
        val = json.loads(val)
    return val


@logger.catch()
async def set_contacts_pagination_page(user_id, new_page):
    key = f"contacts:{user_id}:page"
    await r_async.set(key, new_page, ex=settings.REDIS_RECORD_LIFETIME)


@logger.catch()
async def get_contacts_pagination_page(user_id):
    key = f"contacts:{user_id}:page"
    value = await r_async.get(key)
    return value