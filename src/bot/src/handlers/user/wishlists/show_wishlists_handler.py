from aiogram import Router, types, F
from loguru import logger

from src.database.connection_redis import r_async
from src.database.queries.wishlists.wishlists_sql import get_user_wishlists_list_sql_query
from src.handlers.user.wishlists.inline import (
    wishlists_select_keyboard,
    wishlists_list_keyboard,
    wishlists_keyboard
)
from src.handlers.user.wishlists.redis import (
    get_wishlists_button_callback,
    set_wishlists_pagination_page
)
from src.handlers.user.wishlists.utils import (
    get_wishlists_on_page,
    get_wishlist_message_func
)
from src.keyboards.config import GeneralKb
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="show_wishlists")
router.message.middleware(ThrottlingMiddleware(redis_=r_async))


async def show_wishlists_func(user_id, wishlist_type):
    if wishlist_type == 'me':
        message_text = '🪄 <b>Твои вишлисты</b>'
        page = 1
        user_wishlists_list = await get_user_wishlists_list_sql_query(user_id=user_id, contact_id=user_id)

        wishlists_on_page = get_wishlists_on_page(wishlists_list=user_wishlists_list, page=page)

        await set_wishlists_pagination_page(user_id=user_id, new_page=page)

        return message_text, wishlists_on_page
    else:
        message_text = '🪄 <b>Другие вишлисты</b>'
        page = 1
        user_wishlists_list = await get_user_wishlists_list_sql_query(user_id=user_id, contact_id=0)

        wishlists_on_page = get_wishlists_on_page(wishlists_list=user_wishlists_list, page=page)

        await set_wishlists_pagination_page(user_id=user_id, new_page=page)

        return message_text, wishlists_on_page


@router.message(F.text.lower().in_({'вишлисты', '🪄 вишлисты'}))
async def show_wishlists_cmd(message: types.Message):
    user_id: int = message.from_user.id

    message_text = ('🪄 <b>Твои вишлисты</b>\n'
                    '<code>················</code>\n'
                    '<i>Выбери категорию вишлистов.</i>')

    await message.answer(text=message_text,
                         reply_markup=await wishlists_select_keyboard(user_id=user_id))

    logger.debug(f'{user_id} -> отобразил вишлисты.')


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'sel_wishlists'))
async def call_show_wishlists(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)
    result = await get_wishlists_button_callback(uuid_key=uuid_key)
    if not result:
        try:
            await call.message.delete()
        except Exception as err:
            logger.warning(err)
        return

    user_id = result['user_id']
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


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'sel_wish'))
async def call_show_wishlists(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)
    result = await get_wishlists_button_callback(uuid_key=uuid_key)
    if not result:
        try:
            await call.message.delete()
        except Exception as err:
            logger.warning(err)
        return

    user_id = result['user_id']
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
