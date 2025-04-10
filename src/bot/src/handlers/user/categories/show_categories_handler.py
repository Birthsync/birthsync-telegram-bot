from aiogram import Router, types, F
from loguru import logger

from src.database.connection_redis import r_async
from src.database.queries.categories.categories_sql import get_user_categories_list_sql_query
from src.handlers.user.categories.inline import categories_list_keyboard
from src.handlers.user.categories.redis import set_categories_pagination_page
from src.handlers.user.categories.utils import get_categories_on_page
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="categories")
router.message.middleware(ThrottlingMiddleware(redis_=r_async))


async def show_categories_func(user_id):
    message_text = '🗂 <b>Твои категории</b>'

    page = 1
    user_categories_list = await get_user_categories_list_sql_query(user_id=user_id)

    categories_on_page = get_categories_on_page(categories_list=user_categories_list, page=page)

    await set_categories_pagination_page(user_id=user_id, new_page=page)

    return message_text, categories_on_page


@router.message(F.text.lower().in_({'категории', '🗂 категории'}))
async def show_categories_cmd(message: types.Message):
    user_id: int = message.from_user.id

    message_text, categories_on_page = await show_categories_func(user_id=user_id)

    await message.answer(text=message_text,
                         reply_markup=await categories_list_keyboard(user_id=user_id,
                                                                     categories_on_page=categories_on_page))

    logger.debug(f'{user_id} -> отобразил свои категории.')
