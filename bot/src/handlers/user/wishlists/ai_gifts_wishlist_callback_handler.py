import json

from aiogram import F
from aiogram import Router, types
from loguru import logger

from ai.test_ai import ai_gifts_generator
from src.database.connection_redis import r_async
from src.database.queries.categories.categories_sql import get_category_name_sql_query
from src.database.queries.wishlists.wishlists_sql import get_user_wishlist_data_sql_query
from src.handlers.user.wishlists.inline import (
    ai_gifts_generator_keyboard
)
from src.handlers.user.wishlists.redis import (
    get_wishlists_button_callback
)
from src.handlers.user.wishlists.utils import get_ai_gifts_gen_message_func
from src.keyboards.config import GeneralKb
from src.middlewares.throttling import ThrottlingMiddleware
from src.utils.general_utils import birthdate_from_unix_timestamp

router = Router(name="ai_gifts_wishlist")
router.callback_query.middleware(ThrottlingMiddleware(redis_=r_async))


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'ai_gifts_gen'))
async def call_show_ai_gifts_generator_menu(call: types.CallbackQuery, callback_data: GeneralKb):
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

    message_text = await get_ai_gifts_gen_message_func(user_id=user_id, wishlist_id=wishlist_id)

    await call.message.edit_text(text=message_text,
                                 reply_markup=await ai_gifts_generator_keyboard(user_id=user_id,
                                                                                wishlist_id=wishlist_id,
                                                                                wishlist_type=wishlist_type))
    return


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'generate_gifts'))
async def call_generate_gifts(call: types.CallbackQuery, callback_data: GeneralKb):
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

    wishlist_data = await get_user_wishlist_data_sql_query(user_id=user_id, wishlist_id=wishlist_id)
    wishlist_data = json.loads(wishlist_data)

    first_name = wishlist_data['first_name']
    last_name = wishlist_data['last_name']
    middle_name = wishlist_data['middle_name']
    birthdate = wishlist_data['birthdate']
    categories = wishlist_data['categories']

    birthdate = birthdate_from_unix_timestamp(timestamp=birthdate)

    fio = f'{last_name} {first_name} {middle_name}'

    categories_list = ''

    for category in list(categories.items()):
        category_id = int(category[0])
        category_val = category[1]

        category_name = await get_category_name_sql_query(category_id=category_id)

        categories_list += f'{category_name}: {category_val}; '

    data = {
        'fio': fio,
        'birthdate': birthdate,
        'categories': categories_list
    }

    message_text = ('🌟 <b>Нейро-генератор подарков</b>\n'
                    '<code>················</code>\n'
                    'Ожидайте...')

    await call.message.edit_text(text=message_text)

    result = await ai_gifts_generator(data=data)

    message_text = ('🌟 <b>Нейро-генератор подарков</b>\n'
                    '<code>················</code>\n'
                    f'<blockquote extended>{result}</blockquote>')

    await call.message.edit_text(text=message_text,
                                 reply_markup=await ai_gifts_generator_keyboard(user_id=user_id,
                                                                                wishlist_id=wishlist_id,
                                                                                wishlist_type=wishlist_type))
    return
