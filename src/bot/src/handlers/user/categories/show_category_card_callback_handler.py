from aiogram import F
from aiogram import Router, types
from loguru import logger

from src.database.connection_redis import r_async
from src.database.queries.categories.categories_sql import get_category_name_sql_query, get_category_desc_sql_query
from src.handlers.user.categories.inline import (
    back_category_keyboard
)
from src.handlers.user.categories.redis import (
    get_categories_button_callback
)
from src.keyboards.config import GeneralKb
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="show_category_card")
router.callback_query.middleware(ThrottlingMiddleware(redis_=r_async))


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'select_cat'))
async def call_show_category_card(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)
    result = await get_categories_button_callback(uuid_key=uuid_key)
    if not result:
        try:
            await call.message.delete()
        except Exception as err:
            logger.warning(err)
        return

    user_id = result['user_id']
    category_id = result['category_id']

    category_name = await get_category_name_sql_query(category_id=category_id)
    category_desc = await get_category_desc_sql_query(category_id=category_id)

    text_message = (f'<b>{category_name}</b>\n'
                    f'<code>················</code>\n'
                    f'<i>{category_desc}</i>')

    try:
        await call.message.edit_text(text=text_message,
                                     reply_markup=await back_category_keyboard(user_id=user_id))
    except Exception as err:
        logger.warning(err)
        return
