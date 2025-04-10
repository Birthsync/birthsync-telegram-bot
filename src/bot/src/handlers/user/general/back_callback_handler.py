from aiogram import F
from aiogram import Router, types
from loguru import logger

from src.database.connection_redis import r_async
from src.database.queries.categories.categories_sql import get_user_categories_list_sql_query
from src.handlers.user.categories.inline import categories_list_keyboard
from src.handlers.user.categories.redis import set_categories_pagination_page
from src.handlers.user.categories.show_categories_handler import show_categories_func
from src.handlers.user.categories.utils import get_categories_on_page
from src.handlers.user.general.redis import get_general_button_callback
from src.handlers.user.wishlists.inline import (
    wishlists_select_keyboard,
    wishlists_list_keyboard,
    wishlists_other_keyboard,
    wishlist_creation_keyboard,
    wishlist_categories_list_keyboard, wishlists_keyboard
)
from src.handlers.user.wishlists.show_wishlists_handler import show_wishlists_func
from src.handlers.user.wishlists.utils import get_add_wishlist_message_func, get_wishlist_message_func
from src.keyboards.config import GeneralKb
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="add_wishlist")
router.callback_query.middleware(ThrottlingMiddleware(redis_=r_async))


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'back'))
async def call_select_wishlist_category(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)
    result = await get_general_button_callback(uuid_key=uuid_key)
    if not result:
        try:
            await call.message.delete()
        except Exception as err:
            logger.warning(err)
        return

    user_id = result['user_id']
    backstate = result['backstate']

    if backstate == 1:
        message_text, categories_on_page = await show_categories_func(user_id=user_id)

        try:
            await call.message.edit_text(text=message_text,
                                         reply_markup=await categories_list_keyboard(user_id=user_id,
                                                                                     categories_on_page=categories_on_page))

            logger.debug(f'{user_id} -> отобразил свои категории.')
        except Exception as err:
            logger.warning(err)
            return

    if backstate == 2:
        message_text = ('🪄 <b>Твои вишлисты</b>\n'
                        '<code>················</code>\n'
                        '<i>Выбери категорию вишлистов.</i>')

        try:
            await call.message.edit_text(text=message_text,
                                         reply_markup=await wishlists_select_keyboard(user_id=user_id))
            logger.debug(f'{user_id} -> отобразил вишлисты.')
        except Exception as err:
            logger.warning(err)
            return

    if backstate == 3:
        wishlist_type = result['wishlist_type']

        message_text, wishlists_on_page = await show_wishlists_func(user_id=user_id, wishlist_type=wishlist_type)

        try:
            await call.message.edit_text(text=message_text,
                                         reply_markup=await wishlists_list_keyboard(user_id=user_id,
                                                                                    wishlists_on_page=wishlists_on_page,
                                                                                    wishlist_type=wishlist_type))
        except Exception as err:
            logger.warning(err)
            return

    if backstate == 4:
        message_text = ('<b>Выбери, для кого ты хочешь\n'
                        'создать новый вишлист.</b>')
        try:
            await call.message.edit_text(text=message_text,
                                         reply_markup=await wishlists_other_keyboard(user_id=user_id))

            return
        except Exception as err:
            logger.warning(err)
            return

    if backstate == 5:
        wishlist_type = result['wishlist_type']

        text_field = ('Для изменения параметра, напишите\n'
                      'его в ответ на это сообщение с\n'
                      'указанием нового значения.')
        message_text = await get_add_wishlist_message_func(user_id=user_id, text_field=text_field)

        categories_on_page = []

        try:
            await call.message.edit_text(text=message_text,
                                         reply_markup=await wishlist_creation_keyboard(user_id=user_id,
                                                                                       categories_on_page=categories_on_page,
                                                                                       wishlist_type=wishlist_type))
        except Exception as err:
            logger.warning(err)
            return

    if backstate == 6:
        wishlist_type = result['wishlist_type']

        message_text = '🗂 <b>Выбери категорию</b>'

        page = 1
        user_categories_list = await get_user_categories_list_sql_query(user_id=user_id)

        categories_on_page = get_categories_on_page(categories_list=user_categories_list, page=page)

        await set_categories_pagination_page(user_id=user_id, new_page=page)

        try:
            await call.message.edit_text(text=message_text,
                                         reply_markup=await wishlist_categories_list_keyboard(user_id=user_id,
                                                                                              categories_on_page=categories_on_page,
                                                                                              wishlist_type=wishlist_type))
        except Exception as err:
            logger.warning(err)
            return

    if backstate == 7:
        wishlist_id = result['wishlist_id']
        wishlist_type = result['wishlist_type']

        message_text = await get_wishlist_message_func(user_id=user_id, wishlist_id=wishlist_id)

        try:
            await call.message.edit_text(text=message_text,
                                         reply_markup=await wishlists_keyboard(user_id=user_id,
                                                                               wishlist_type=wishlist_type,
                                                                               wishlist_id=wishlist_id))
        except Exception as err:
            logger.warning(err)
            return
