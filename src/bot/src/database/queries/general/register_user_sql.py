import html
import json
import time

from aiogram import types
from loguru import logger
from src.database.context_manager import db_cursor


@logger.catch()
async def register_new_user_transaction_sql_query(message: types.Message):
    try:
        async with db_cursor() as cursor:
            user_id = message.from_user.id
            username = message.from_user.username or None
            fullname = str(html.escape(message.from_user.full_name))
            email = None
            phone_number = None
            is_active = True
            is_premium = False
            is_superuser = False
            created_at = int(time.time())

            res = await cursor.fetchval("INSERT INTO users(user_id, username, fullname, email, phone_number, "
                                        "is_active, is_premium, is_superuser, created_at) "
                                        "VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9) "
                                        "ON CONFLICT (user_id) DO NOTHING "
                                        "RETURNING id",
                                        user_id, username, fullname, email, phone_number, is_active,
                                        is_premium, is_superuser, created_at)

            user_first_name = message.from_user.first_name
            user_last_name = message.from_user.last_name
            user_middle_name = None
            user_birthdate = message.chat.birthdate

            await cursor.execute("INSERT INTO user_cards(user_id, first_name, last_name, middle_name, birthdate) "
                                 "VALUES ($1, $2, $3, $4, $5) "
                                 "ON CONFLICT (user_id) DO NOTHING",
                                 user_id, user_first_name, user_last_name, user_middle_name, user_birthdate)

            contact_id = user_id
            data = {}
            wishlist_data = json.dumps(data)

            await cursor.execute("INSERT INTO wishlists(user_id, contact_id, data) "
                                 "VALUES($1, $2, $3) ",
                                 user_id, contact_id, wishlist_data)
    except Exception as err:
        logger.warning(err)
        return
    logger.success(f'✅ Пользователь @{username} ({user_id}) успешно зарегистрировался (#{res}).')
