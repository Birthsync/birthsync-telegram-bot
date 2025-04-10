import uuid

from aiogram import types
from loguru import logger

from src.database.queries.categories.categories_sql import get_category_name_sql_query
from src.handlers.user.categories.config import MAX_CATEGORIES_BUTTONS_ON_PAGE
from src.handlers.user.categories.redis import set_categories_button_callback, get_categories_params
from src.keyboards.config import GeneralKb


@logger.catch()
async def categories_list_keyboard(user_id, categories_on_page):
    keyboard = []
    row = []

    data = {
        'user_id': user_id,
    }

    uuid_key = str(uuid.uuid4())
    await set_categories_button_callback(uuid_key=uuid_key, data=data)

    for category in categories_on_page:
        category_id = category[0]
        data = {
            'user_id': user_id,
            'category_id': category_id,
        }
        uuid_key_category = str(uuid.uuid4())
        await set_categories_button_callback(uuid_key=uuid_key_category, data=data)

        category_name = await get_category_name_sql_query(category_id=category_id)

        row.append(types.InlineKeyboardButton(text=f'{category_name}',
                                              callback_data=GeneralKb(action=f'select_cat',
                                                                      uuid_key=uuid_key_category).pack()))
        keyboard.append(row)
        row = []

    if len(categories_on_page) > MAX_CATEGORIES_BUTTONS_ON_PAGE:
        row = [types.InlineKeyboardButton(text=f'«',
                                          callback_data=GeneralKb(action='cat_pag_back',
                                                                  uuid_key=uuid_key).pack()),
               types.InlineKeyboardButton(text=f'»',
                                          callback_data=GeneralKb(action='cat_pag_next',
                                                                  uuid_key=uuid_key).pack())]
        keyboard.append(row)

    row = [types.InlineKeyboardButton(text='➕ Добавить',
                                      callback_data=GeneralKb(action='show_avail_cat',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Закрыть',
                                      callback_data=GeneralKb(action='close',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@logger.catch()
async def create_category_keyboard(user_id):
    keyboard = []

    data = await get_categories_params(user_id=user_id) or {}
    category_name = data.get('category_name') or None

    data = {
        'user_id': user_id,
        'backstate': 1
    }

    uuid_key = str(uuid.uuid4())
    await set_categories_button_callback(uuid_key=uuid_key, data=data)

    if category_name is not None:
        row = [types.InlineKeyboardButton(text=f'✔ Создать',
                                          callback_data=GeneralKb(action=f'create_category',
                                                                  uuid_key=uuid_key).pack())]
        keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Назад',
                                      callback_data=GeneralKb(action='back',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@logger.catch()
async def back_category_keyboard(user_id):
    keyboard = []

    data = {
        'user_id': user_id,
        'backstate': 1,
    }

    uuid_key = str(uuid.uuid4())
    await set_categories_button_callback(uuid_key=uuid_key, data=data)

    row = [types.InlineKeyboardButton(text='Назад',
                                      callback_data=GeneralKb(action='back',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)