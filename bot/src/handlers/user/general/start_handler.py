import html

from aiogram import Router, types
from aiogram.filters import CommandStart
from loguru import logger

from src.database.connection_redis import r_async
from src.database.queries.general.general_sql import get_user_exists_sql_query
from src.keyboards.general_kb import main_keyboard
from src.middlewares.throttling import ThrottlingMiddleware
from src.database.queries.general.register_user_sql import register_new_user_transaction_sql_query


router = Router(name="start")
router.message.middleware(ThrottlingMiddleware(redis_=r_async))


@router.message(CommandStart())
async def start_cmd(message: types.Message):
    user_id: int = message.from_user.id
    fullname = str(html.escape(message.from_user.full_name))

    if await get_user_exists_sql_query(user_id=user_id):
        if message.chat.type == 'private':
            await register_new_user_transaction_sql_query(message=message)
            return

    await message.answer(text=f'Привет, {fullname}!',
                         reply_markup=await main_keyboard())

    logger.debug(f'{user_id} -> использовал /start')
