import uuid

from aiogram import types
from loguru import logger

from src.handlers.user.contacts.redis import set_contacts_button_callback
from src.keyboards.config import GeneralKb


@logger.catch()
async def add_contact_keyboard(user_id, contact_id):
    keyboard = []

    data = {
        'user_id': user_id,
        'contact_id': contact_id,
    }

    uuid_key = str(uuid.uuid4())
    await set_contacts_button_callback(uuid_key=uuid_key, data=data)

    row = [types.InlineKeyboardButton(text='✅',
                                      callback_data=GeneralKb(action='add_contact_accept',
                                                              uuid_key=uuid_key).pack()),
           types.InlineKeyboardButton(text='❌',
                                      callback_data=GeneralKb(action='add_contact_reject',
                                                              uuid_key=uuid_key).pack())
           ]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
