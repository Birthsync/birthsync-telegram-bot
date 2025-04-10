import re

from aiogram import types, Router, F
from loguru import logger

from loader import bot
from src.database.connection_redis import r_async
from src.handlers.user.categories.add_category_callback_handler import change_category_params_func
from src.handlers.user.categories.redis import get_categories_button_callback
from src.handlers.user.wishlists.add_wishlist_callback_handler import change_wishlist_params_func, change_wishlist_category_params_func
from src.handlers.user.wishlists.redis import get_wishlists_button_callback
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="messages")
router.message.middleware(ThrottlingMiddleware(redis_=r_async))


async def check_category_params(message):
    try:
        bot_info = await bot.get_me()
        bot_id = bot_info.id
        if message.reply_to_message and message.reply_to_message.reply_markup:
            if ('🗂 Создание категории' in message.reply_to_message.text) and (message.reply_to_message.from_user.id == bot_id):
                button = message.reply_to_message.reply_markup.inline_keyboard[0][0]
                callback_data = button.callback_data
                match = re.search(r'general:(.+):(.+)', callback_data)
                if match:
                    action = str(match.group(1))
                    uuid_key = str(match.group(2))
                    if action in ('back', 'create_category'):
                        data = await get_categories_button_callback(uuid_key=uuid_key)
                        if not data:
                            logger.warning(f"No data found for uuid_key: {uuid_key}")
                            await bot.delete_message(chat_id=message.chat.id,
                                                     message_id=message.reply_to_message.message_id)
                            return

                        user_id = int(data.get('user_id'))
                        if message.from_user.id == user_id:
                            await change_category_params_func(message=message, user_id=user_id)
    except Exception as err:
        logger.warning(err)


async def check_wishlist_params(message):
    try:
        bot_info = await bot.get_me()
        bot_id = bot_info.id
        if message.reply_to_message and message.reply_to_message.reply_markup:
            if ('🪄 Создание вишлиста' in message.reply_to_message.text) and (message.reply_to_message.from_user.id == bot_id):
                button = message.reply_to_message.reply_markup.inline_keyboard[0][0]
                callback_data = button.callback_data
                match = re.search(r'general:(.+):(.+)', callback_data)
                if match:
                    action = str(match.group(1))
                    uuid_key = str(match.group(2))
                    if action in ('back', 'create_wish', 'show_wish_cats'):
                        data = await get_wishlists_button_callback(uuid_key=uuid_key)
                        if not data:
                            logger.warning(f"No data found for uuid_key: {uuid_key}")
                            await bot.delete_message(chat_id=message.chat.id,
                                                     message_id=message.reply_to_message.message_id)
                            return

                        user_id = int(data.get('user_id'))
                        wishlist_type = str(data.get('wishlist_type'))
                        if message.from_user.id == user_id:
                            await change_wishlist_params_func(message=message,
                                                              user_id=user_id,
                                                              wishlist_type=wishlist_type)
    except Exception as err:
        logger.warning(err)


async def check_wishlist_category_params(message):
    try:
        bot_info = await bot.get_me()
        bot_id = bot_info.id
        if message.reply_to_message and message.reply_to_message.reply_markup:
            if ('🗂 Добавление категории' in message.reply_to_message.text) and (message.reply_to_message.from_user.id == bot_id):
                button = message.reply_to_message.reply_markup.inline_keyboard[0][0]
                callback_data = button.callback_data
                match = re.search(r'general:(.+):(.+)', callback_data)
                if match:
                    action = str(match.group(1))
                    uuid_key = str(match.group(2))
                    if action in ('back', 'add_wish_cat'):
                        data = await get_wishlists_button_callback(uuid_key=uuid_key)
                        if not data:
                            logger.warning(f"No data found for uuid_key: {uuid_key}")
                            await bot.delete_message(chat_id=message.chat.id,
                                                     message_id=message.reply_to_message.message_id)
                            return

                        user_id = int(data.get('user_id'))
                        category_id = int(data.get('category_id'))
                        wishlist_type = str(data.get('wishlist_type'))
                        if message.from_user.id == user_id:
                            await change_wishlist_category_params_func(message=message,
                                                                       user_id=user_id,
                                                                       category_id=category_id,
                                                                       wishlist_type=wishlist_type)
    except Exception as err:
        logger.warning(err)


@router.message(F.text)
async def messages(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    user_text = message.text
    chat_type = message.chat.type

    await check_category_params(message=message)
    await check_wishlist_params(message=message)
    await check_wishlist_category_params(message=message)