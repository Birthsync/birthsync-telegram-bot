from aiogram import F
from aiogram import Router, types
from loguru import logger

from src.database.connection_redis import r_async
from src.keyboards.config import GeneralKb
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="close")
router.callback_query.middleware(ThrottlingMiddleware(redis_=r_async))


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'close'))
async def call_close(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)

    try:
        await call.message.delete()
    except Exception as err:
        logger.warning(err)
    return
