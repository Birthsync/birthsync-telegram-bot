import uuid

from aiogram import types
from loguru import logger

from src.database.queries.user_card.user_card_sql import get_user_first_name_sql_query
from src.handlers.user.contacts.config import MAX_CONTACTS_BUTTONS_ON_PAGE
from src.handlers.user.contacts.redis import set_contacts_button_callback
from src.keyboards.config import GeneralKb


@logger.catch()
async def contacts_list_keyboard(user_id, contacts_on_page):
    keyboard = []
    row = []

    data = {
        'user_id': user_id,
    }

    uuid_key = str(uuid.uuid4())
    await set_contacts_button_callback(uuid_key=uuid_key, data=data)

    for contact in contacts_on_page:
        contact_id = contact[0]
        data = {
            'user_id': user_id,
            'contact_id': contact_id,
        }
        uuid_key_contact = str(uuid.uuid4())
        await set_contacts_button_callback(uuid_key=uuid_key_contact, data=data)

        contact_firstname = await get_user_first_name_sql_query(user_id=contact_id)

        row.append(types.InlineKeyboardButton(text=f'{contact_firstname}',
                                              callback_data=GeneralKb(action=f'sel_contact',
                                                                      uuid_key=uuid_key_contact).pack()))
        keyboard.append(row)
        row = []

    if len(contacts_on_page) > MAX_CONTACTS_BUTTONS_ON_PAGE:
        row = [types.InlineKeyboardButton(text=f'«',
                                          callback_data=GeneralKb(action='cont_pag_back',
                                                                  uuid_key=uuid_key).pack()),
               types.InlineKeyboardButton(text=f'»',
                                          callback_data=GeneralKb(action='cont_pag_next',
                                                                  uuid_key=uuid_key).pack())]
        keyboard.append(row)

    row = [types.InlineKeyboardButton(text='➕ Добавить', switch_inline_query='\n\nПривет! Добавляйся ко мне в контакты!\n\n'
                                                                             f'Жми на ссылку: t.me/birthsync_bot?start=add_{user_id}')]
    keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Закрыть',
                                      callback_data=GeneralKb(action='close',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
