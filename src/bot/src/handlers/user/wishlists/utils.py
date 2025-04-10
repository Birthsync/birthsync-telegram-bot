import json

from loguru import logger

from src.database.queries.categories.categories_sql import get_category_name_sql_query, get_category_desc_sql_query
from src.database.queries.user_card.user_card_sql import get_user_card_info_sql_query
from src.database.queries.wishlists.wishlists_sql import get_user_wishlist_data_sql_query
from src.handlers.user.wishlists.config import MAX_WISHLISTS_BUTTONS_ON_PAGE
from src.handlers.user.wishlists.redis import set_wishlist_params, get_wishlist_params, get_wishlist_category_params
from src.utils.general_utils import birthdate_from_unix_timestamp, insert_line_breaks


async def wishlist_creation_func(user_id, contact_id):
    try:
        result = await get_user_card_info_sql_query(user_id=contact_id) or []
        first_name = result[0] or ''
        last_name = result[1] or ''
        middle_name = result[2] or ''
        birthdate = result[3] or ''
    except IndexError:
        first_name = last_name = middle_name = birthdate = ''

    data = {
        'contact_id': contact_id,
        'first_name': first_name,
        'last_name': last_name,
        'middle_name': middle_name,
        'birthdate': birthdate,
        'categories': {}
    }
    await set_wishlist_params(user_id=user_id, data=data)


async def get_add_wishlist_message_func(user_id, text_field):
    message_text = ('🪄 <b>Создание вишлиста</b>\n'
                    '<code>················</code>\n')

    data = await get_wishlist_params(user_id=user_id)

    first_name = data['first_name']
    last_name = data['last_name']
    middle_name = data['middle_name']
    birthdate = data['birthdate']
    categories = data['categories']

    birthdate = birthdate_from_unix_timestamp(timestamp=birthdate)

    message_text += (f'<b>Имя :</b>  <code>{first_name}</code>\n'
                     f'<b>Фамилия :</b>  <code>{last_name}</code>\n'
                     f'<b>Отчество :</b>  <code>{middle_name}</code>\n'
                     f'<b>Дата рождения:</b>  <code>{birthdate}</code>\n')

    categories_text = ''

    num = 0
    for category in list(categories.items()):
        category_id = int(category[0])
        category_val = category[1]

        if num > 0:
            categories_text += '\n'
        category_name = await get_category_name_sql_query(category_id=category_id)

        category_val = insert_line_breaks(category_val)

        categories_text += (f'<b>{category_name}:</b>\n'
                            f'<i>{category_val}</i>\n')
        num += 1

    if categories_text != '':
        categories_text = ('<code>················</code>\n'
                           '<blockquote expandable>') + categories_text + '</blockquote>'

    message_text += categories_text

    message_text += ('<code>················</code>\n'
                     f'<i>{text_field}</i>\n'
                     '<code>················</code>\n'
                     '<blockquote>Пример 1:  <code>имя Мирослав</code>\n'
                     'Пример 2:  <code>дата 11.09.2001</code></blockquote>')

    return message_text


async def get_add_wishlist_category_message_func(user_id, category_id, text_field):
    message_text = (f'<b>🗂 Добавление категории</b>\n'
                    f'<code>················</code>\n')

    category_name = await get_category_name_sql_query(category_id=category_id)
    category_desc = await get_category_desc_sql_query(category_id=category_id)

    category_desc = insert_line_breaks(category_desc)

    message_text += (f'<b>{category_name}</b>\n'
                     f'<i>{category_desc}</i>\n'
                     f'<code>················</code>\n')

    category_data = await get_wishlist_category_params(user_id=user_id) or {}
    category_val = category_data.get('category_val') or ''

    category_val = insert_line_breaks(category_val)

    if category_val != '':
        category_val += '\n'

    message_text += (f'<b>Содержимое:</b>\n'
                     f'<i>{category_val}</i>')

    message_text += (f'<code>················</code>\n'
                     f'<i>{text_field}</i>\n'
                     f'<code>················</code>\n'
                     f'<blockquote>Пример: <code>Книга по Вархаммер 40000</code></blockquote>')

    return message_text


async def get_wishlist_message_func(user_id, wishlist_id):

    wishlist_data = await get_user_wishlist_data_sql_query(user_id=user_id, wishlist_id=wishlist_id)
    wishlist_data = json.loads(wishlist_data)

    first_name = wishlist_data['first_name']
    last_name = wishlist_data['last_name']
    middle_name = wishlist_data['middle_name']
    birthdate = wishlist_data['birthdate']
    categories = wishlist_data['categories']

    message_text = (f'🪄 <b>Вишлист</b> <code>№{wishlist_id}</code>\n'
                    '<code>················</code>\n')

    birthdate = birthdate_from_unix_timestamp(timestamp=birthdate)

    message_text += (f'<b>Имя :</b>  <code>{first_name}</code>\n'
                     f'<b>Фамилия :</b>  <code>{last_name}</code>\n'
                     f'<b>Отчество :</b>  <code>{middle_name}</code>\n'
                     f'<b>Дата рождения:</b>  <code>{birthdate}</code>\n')

    categories_text = ''

    num = 0
    for category in list(categories.items()):
        category_id = int(category[0])
        category_val = category[1]

        if num > 0:
            categories_text += '\n'
        category_name = await get_category_name_sql_query(category_id=category_id)

        category_val = insert_line_breaks(category_val)

        categories_text += (f'<b>{category_name}:</b>\n'
                            f'<i>{category_val}</i>\n')
        num += 1

    if categories_text != '':
        categories_text = ('<code>················</code>\n'
                           '<blockquote expandable>') + categories_text + '</blockquote>'

    message_text += categories_text

    return message_text


async def get_ai_gifts_gen_message_func(user_id, wishlist_id):
    wishlist_data = await get_user_wishlist_data_sql_query(user_id=user_id, wishlist_id=wishlist_id)
    wishlist_data = json.loads(wishlist_data)

    first_name = wishlist_data['first_name']
    last_name = wishlist_data['last_name']
    middle_name = wishlist_data['middle_name']
    birthdate = wishlist_data['birthdate']
    categories = wishlist_data['categories']

    birthdate = birthdate_from_unix_timestamp(timestamp=birthdate)

    fio = f'{last_name} {first_name} {middle_name}'

    categories_text = ''

    num = 0
    for category in list(categories.items()):
        category_id = int(category[0])
        category_val = category[1]

        if num > 0:
            categories_text += '\n'
        category_name = await get_category_name_sql_query(category_id=category_id)

        category_val = insert_line_breaks(category_val)

        categories_text += (f'<b>{category_name}:</b>\n'
                            f'<i>{category_val}</i>\n')
        num += 1

    if categories_text != '':
        categories_text = '<blockquote expandable>' + categories_text + '</blockquote>'

    message_text = ('🌟 <b>Нейро-генератор подарков</b>\n'
                    '<code>················</code>\n'
                    '<i>Нейро-генератор сможет составить\n'
                    'топ-10 подарков, на основе входных\n'
                    'параметров вишлиста: ФИО, категории\n'
                    'и возраст человека.</i>\n'
                    '<code>················</code>\n'
                    '<b>Входные параметры:</b>\n'
                    f'<b>ФИО :</b>  <code>{fio}</code>\n'
                    f'<b>Дата рождения :</b>  <code>{birthdate}</code>\n'
                    f'{categories_text}')
    return message_text


@logger.catch()
def get_wishlists_on_page(wishlists_list, page):
    start_index = (page - 1) * MAX_WISHLISTS_BUTTONS_ON_PAGE
    end_index = start_index + MAX_WISHLISTS_BUTTONS_ON_PAGE
    wishlists_on_page = wishlists_list[start_index:end_index]
    return wishlists_on_page
