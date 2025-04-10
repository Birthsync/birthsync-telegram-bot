import uuid

from aiogram import types
from loguru import logger

from src.handlers.user.contacts.redis import set_contacts_button_callback
from src.keyboards.config import GeneralKb


@logger.catch()
async def profile_keyboard(user_id):
    keyboard = []

    data = {
        'user_id': user_id,
    }

    uuid_key = str(uuid.uuid4())
    await set_contacts_button_callback(uuid_key=uuid_key, data=data)

    row = [types.InlineKeyboardButton(text='✏ Редактировать',
                                      callback_data=GeneralKb(action='profile_edit',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Закрыть',
                                      callback_data=GeneralKb(action='close',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
