import json
import uuid

from aiogram import types
from loguru import logger

from src.database.queries.categories.categories_sql import get_category_name_sql_query
from src.database.queries.contacts.contacts_sql import get_user_contact_sql_query
from src.database.queries.user_card.user_card_sql import get_user_first_name_sql_query, get_user_last_name_sql_query
from src.database.queries.wishlists.wishlists_sql import get_user_wishlist_data_sql_query
from src.handlers.user.categories.config import MAX_CATEGORIES_BUTTONS_ON_PAGE
from src.handlers.user.contacts.config import MAX_CONTACTS_BUTTONS_ON_PAGE
from src.handlers.user.wishlists.config import MAX_WISHLISTS_BUTTONS_ON_PAGE
from src.handlers.user.wishlists.redis import set_wishlists_button_callback, get_wishlist_params, get_wishlist_category_params
from src.keyboards.config import GeneralKb


@logger.catch()
async def wishlists_select_keyboard(user_id):
    keyboard = []
    row = []

    data = {
        'user_id': user_id,
        'wishlist_type': 'me',
    }
    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    row.append(types.InlineKeyboardButton(text=f'Мои',
                                          callback_data=GeneralKb(action=f'sel_wishlists',
                                                                  uuid_key=uuid_key).pack()))

    data = {
        'user_id': user_id,
        'wishlist_type': 'other'
    }
    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    row.append(types.InlineKeyboardButton(text=f'Другие',
                                          callback_data=GeneralKb(action=f'sel_wishlists',
                                                                  uuid_key=uuid_key).pack()))

    keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Закрыть',
                                      callback_data=GeneralKb(action='close',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@logger.catch()
async def wishlists_list_keyboard(user_id, wishlists_on_page, wishlist_type):
    keyboard = []
    row = []

    data = {
        'user_id': user_id,
        'wishlist_type': wishlist_type,
        'backstate': 2
    }

    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    for wishlist in wishlists_on_page:
        wishlist_id = wishlist[0]
        data = {
            'user_id': user_id,
            'wishlist_id': wishlist_id,
            'wishlist_type': wishlist_type,
        }
        uuid_key_wishlist = str(uuid.uuid4())
        await set_wishlists_button_callback(uuid_key=uuid_key_wishlist, data=data)

        wishlist_data = await get_user_wishlist_data_sql_query(user_id=user_id, wishlist_id=wishlist_id)
        wishlist_data = json.loads(wishlist_data)
        contact_id = wishlist_data.get('contact_id')
        wishlist_firstname = wishlist_data.get('first_name')
        wishlist_lastname = wishlist_data.get('last_name')

        contact_icon = '👤 ' if await get_user_contact_sql_query(user_id=user_id, contact_id=contact_id) else ''

        row.append(types.InlineKeyboardButton(text=f'{contact_icon}{wishlist_firstname} {wishlist_lastname}',
                                              callback_data=GeneralKb(action=f'sel_wish',
                                                                      uuid_key=uuid_key_wishlist).pack()))
        keyboard.append(row)
        row = []

    if len(wishlists_on_page) > MAX_WISHLISTS_BUTTONS_ON_PAGE:
        row = [types.InlineKeyboardButton(text=f'«',
                                          callback_data=GeneralKb(action='wish_pag_back',
                                                                  uuid_key=uuid_key).pack()),
               types.InlineKeyboardButton(text=f'»',
                                          callback_data=GeneralKb(action='wish_pag_next',
                                                                  uuid_key=uuid_key).pack())]
        keyboard.append(row)

    row = [types.InlineKeyboardButton(text='➕ Добавить',
                                      callback_data=GeneralKb(action='add_wishlist',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Назад',
                                      callback_data=GeneralKb(action='back',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@logger.catch()
async def wishlists_other_keyboard(user_id):
    keyboard = []

    data = {
        'user_id': user_id,
        'wishlist_type': 'contacts',
        'backstate': 3
    }
    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    row = [types.InlineKeyboardButton(text=f'👤 Выбрать контакт',
                                      callback_data=GeneralKb(action=f'add_wishlist',
                                                              uuid_key=uuid_key).pack())]

    keyboard.append(row)

    data = {
        'user_id': user_id,
        'wishlist_type': 'no_contacts',
        'backstate': 3
    }
    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    row = [types.InlineKeyboardButton(text=f'Не в контактах',
                                      callback_data=GeneralKb(action=f'add_wishlist',
                                                              uuid_key=uuid_key).pack())]

    keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Назад',
                                      callback_data=GeneralKb(action='back',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@logger.catch()
async def wishlist_contacts_list_keyboard(user_id, contacts_on_page):
    keyboard = []
    row = []

    data = {
        'user_id': user_id,
        'backstate': 4
    }

    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    for contact in contacts_on_page:
        contact_id = contact[0]
        data = {
            'user_id': user_id,
            'contact_id': contact_id,
            'wishlist_type': 'contact'
        }
        uuid_key_contact = str(uuid.uuid4())
        await set_wishlists_button_callback(uuid_key=uuid_key_contact, data=data)

        contact_firstname = await get_user_first_name_sql_query(user_id=contact_id)
        contact_lastname = await get_user_last_name_sql_query(user_id=contact_id)
        contact_lastname = f' {contact_lastname}' if contact_lastname else ''

        row.append(types.InlineKeyboardButton(text=f'{contact_firstname}{contact_lastname}',
                                              callback_data=GeneralKb(action=f'add_wishlist',
                                                                      uuid_key=uuid_key_contact).pack()))
        keyboard.append(row)
        row = []

    if len(contacts_on_page) > MAX_CONTACTS_BUTTONS_ON_PAGE:
        row = [types.InlineKeyboardButton(text=f'«',
                                          callback_data=GeneralKb(action='cont_wish_pag_back',
                                                                  uuid_key=uuid_key).pack()),
               types.InlineKeyboardButton(text=f'»',
                                          callback_data=GeneralKb(action='cont_wish_pag_next',
                                                                  uuid_key=uuid_key).pack())]
        keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Назад',
                                      callback_data=GeneralKb(action='back',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@logger.catch()
async def wishlist_creation_keyboard(user_id, categories_on_page, wishlist_type):
    keyboard = []
    row = []

    data = {
        'user_id': user_id,
        'wishlist_type': wishlist_type,
        'backstate': 2
    }

    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    for category in categories_on_page:
        category_id = category[0]
        data = {
            'user_id': user_id,
            'category_id': category_id,
        }
        uuid_key_category = str(uuid.uuid4())
        await set_wishlists_button_callback(uuid_key=uuid_key_category, data=data)

        category_name = await get_category_name_sql_query(category_id=category_id)

        row.append(types.InlineKeyboardButton(text=f'{category_name}',
                                              callback_data=GeneralKb(action=f'edit_wish_cat',
                                                                      uuid_key=uuid_key_category).pack()))
        keyboard.append(row)
        row = []

    if len(categories_on_page) > MAX_CATEGORIES_BUTTONS_ON_PAGE:
        row = [types.InlineKeyboardButton(text=f'«',
                                          callback_data=GeneralKb(action='cats_wish_pag_back',
                                                                  uuid_key=uuid_key).pack()),
               types.InlineKeyboardButton(text=f'»',
                                          callback_data=GeneralKb(action='cats_wish_pag_next',
                                                                  uuid_key=uuid_key).pack())]
        keyboard.append(row)

    data = await get_wishlist_params(user_id=user_id) or {}
    first_name = data.get('first_name') or ''
    categories = data.get('categories') or {}

    if (first_name != '') and (len(list(categories.keys())) != 0):
        row = [types.InlineKeyboardButton(text='✔ Создать',
                                          callback_data=GeneralKb(action='create_wish',
                                                                  uuid_key=uuid_key).pack())]
        keyboard.append(row)

    row = [types.InlineKeyboardButton(text='🗂 Категории',
                                      callback_data=GeneralKb(action='show_wish_cats',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Отмена',
                                      callback_data=GeneralKb(action='back',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@logger.catch()
async def wishlist_categories_list_keyboard(user_id, categories_on_page, wishlist_type):
    keyboard = []
    row = []

    data = {
        'user_id': user_id,
        'wishlist_type': wishlist_type,
        'backstate': 5
    }

    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    for category in categories_on_page:
        category_id = category[0]
        data = {
            'user_id': user_id,
            'category_id': category_id,
            'wishlist_type': wishlist_type
        }
        uuid_key_wishlist = str(uuid.uuid4())
        await set_wishlists_button_callback(uuid_key=uuid_key_wishlist, data=data)

        category_name = await get_category_name_sql_query(category_id=category_id)

        row.append(types.InlineKeyboardButton(text=f'{category_name}',
                                              callback_data=GeneralKb(action=f'sel_wish_cat',
                                                                      uuid_key=uuid_key_wishlist).pack()))
        keyboard.append(row)
        row = []

    if len(categories_on_page) > MAX_CATEGORIES_BUTTONS_ON_PAGE:
        row = [types.InlineKeyboardButton(text=f'«',
                                          callback_data=GeneralKb(action='cat_wish_pag_back',
                                                                  uuid_key=uuid_key).pack()),
               types.InlineKeyboardButton(text=f'»',
                                          callback_data=GeneralKb(action='cat_wish_pag_next',
                                                                  uuid_key=uuid_key).pack())]
        keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Назад',
                                      callback_data=GeneralKb(action='back',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@logger.catch()
async def wishlist_add_category_keyboard(user_id, category_id, wishlist_type):
    keyboard = []

    data = {
        'user_id': user_id,
        'category_id': category_id,
        'wishlist_type': wishlist_type,
        'backstate': 6
    }

    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    category_data = await get_wishlist_category_params(user_id=user_id) or {}
    category_val = category_data.get('category_val') or ''

    if category_val != '':
        row = [types.InlineKeyboardButton(text='➕ Добавить',
                                          callback_data=GeneralKb(action='add_wish_cat',
                                                                  uuid_key=uuid_key).pack())]
        keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Назад',
                                      callback_data=GeneralKb(action='back',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@logger.catch()
async def wishlists_keyboard(user_id, wishlist_type, wishlist_id):
    keyboard = []
    row = []

    data = {
        'user_id': user_id,
        'wishlist_type': wishlist_type,
        'wishlist_id': wishlist_id,
        'backstate': 3
    }
    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    row.append(types.InlineKeyboardButton(text=f'✏',
                                          callback_data=GeneralKb(action=f'wish_edit',
                                                                  uuid_key=uuid_key).pack()))

    row.append(types.InlineKeyboardButton(text=f'🎁',
                                          callback_data=GeneralKb(action=f'wish_gifts',
                                                                  uuid_key=uuid_key).pack()))

    row.append(types.InlineKeyboardButton(text=f'🗑',
                                          callback_data=GeneralKb(action=f'wish_del',
                                                                  uuid_key=uuid_key).pack()))

    keyboard.append(row)

    row = [types.InlineKeyboardButton(text='✨ Подобрать подарки',
                                      callback_data=GeneralKb(action='ai_gifts_gen',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Назад',
                                      callback_data=GeneralKb(action='back',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@logger.catch()
async def ai_gifts_generator_keyboard(user_id, wishlist_type, wishlist_id):
    keyboard = []
    row = []

    data = {
        'user_id': user_id,
        'wishlist_type': wishlist_type,
        'wishlist_id': wishlist_id,
        'backstate': 7
    }
    uuid_key = str(uuid.uuid4())
    await set_wishlists_button_callback(uuid_key=uuid_key, data=data)

    row.append(types.InlineKeyboardButton(text=f'✨ Подобрать ✨',
                                          callback_data=GeneralKb(action=f'generate_gifts',
                                                                  uuid_key=uuid_key).pack()))
    keyboard.append(row)

    row = [types.InlineKeyboardButton(text='Назад',
                                      callback_data=GeneralKb(action='back',
                                                              uuid_key=uuid_key).pack())]
    keyboard.append(row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)
