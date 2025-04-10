import json
import re

from aiogram import F
from aiogram import Router, types
from loguru import logger

from loader import bot
from src.database.connection_redis import r_async
from src.database.queries.categories.categories_sql import get_user_categories_list_sql_query
from src.database.queries.contacts.contacts_sql import get_user_contacts_list_sql_query
from src.database.queries.wishlists.wishlists_sql import create_record_in_wishlists_sql_query
from src.handlers.user.categories.redis import (
    set_categories_pagination_page
)
from src.handlers.user.categories.utils import get_categories_on_page
from src.handlers.user.contacts.redis import set_contacts_pagination_page
from src.handlers.user.contacts.utils import get_contacts_on_page
from src.handlers.user.wishlists.config import (
    MAX_WISHLIST_FIRST_NAME_LEN,
    MAX_WISHLIST_LAST_NAME_LEN,
    MAX_WISHLIST_MIDDLE_NAME_LEN,
    MAX_WISHLIST_CATEGORY_VAL_LEN
)
from src.handlers.user.wishlists.inline import (
    wishlists_other_keyboard,
    wishlist_contacts_list_keyboard,
    wishlist_creation_keyboard,
    wishlist_categories_list_keyboard,
    wishlist_add_category_keyboard,
    wishlists_list_keyboard
)
from src.handlers.user.wishlists.redis import (
    get_wishlists_button_callback,
    get_wishlist_params,
    set_wishlist_params,
    get_wishlist_category_params,
    set_wishlist_category_params
)
from src.handlers.user.wishlists.show_wishlists_handler import show_wishlists_func
from src.handlers.user.wishlists.utils import (
    wishlist_creation_func,
    get_add_wishlist_message_func,
    get_add_wishlist_category_message_func
)
from src.keyboards.config import GeneralKb
from src.middlewares.throttling import ThrottlingMiddleware
from src.utils.general_utils import birthdate_to_unix_timestamp

router = Router(name="add_wishlist")
router.callback_query.middleware(ThrottlingMiddleware(redis_=r_async))


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'show_wish_cats'))
async def call_show_wishlist_categories(call: types.CallbackQuery, callback_data: GeneralKb):
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

    message_text = '🗂 <b>Выбери категорию</b>'

    page = 1
    user_categories_list = await get_user_categories_list_sql_query(user_id=user_id)

    categories_on_page = get_categories_on_page(categories_list=user_categories_list, page=page)

    await set_categories_pagination_page(user_id=user_id, new_page=page)

    await call.message.edit_text(text=message_text,
                                 reply_markup=await wishlist_categories_list_keyboard(user_id=user_id,
                                                                                      categories_on_page=categories_on_page,
                                                                                      wishlist_type=wishlist_type))
    return


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'sel_wish_cat'))
async def call_select_wishlist_category(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)
    result = await get_wishlists_button_callback(uuid_key=uuid_key)
    if not result:
        try:
            await call.message.delete()
        except Exception as err:
            logger.warning(err)
        return

    user_id = result['user_id']
    category_id = result['category_id']
    wishlist_type = result['wishlist_type']

    data = {
        'category_val': '',
    }
    await set_wishlist_category_params(user_id=user_id, data=data)

    text_field = ('Чтобы указать содержимое категории,\n'
                  f'напишите вашу информацию в ответ на\n'
                  f'это сообщение.')

    message_text = await get_add_wishlist_category_message_func(user_id=user_id,
                                                                category_id=category_id,
                                                                text_field=text_field)

    await call.message.edit_text(text=message_text,
                                 reply_markup=await wishlist_add_category_keyboard(user_id=user_id,
                                                                                   category_id=category_id,
                                                                                   wishlist_type=wishlist_type))
    return


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'add_wish_cat'))
async def call_add_wishlist_category(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)
    result = await get_wishlists_button_callback(uuid_key=uuid_key)
    if not result:
        try:
            await call.message.delete()
        except Exception as err:
            logger.warning(err)
        return

    user_id = result['user_id']
    category_id = result['category_id']
    wishlist_type = result['wishlist_type']

    text_field = ('Для изменения параметра, напишите\n'
                  'его в ответ на это сообщение с\n'
                  'указанием нового значения.')

    category_data = await get_wishlist_category_params(user_id=user_id) or {}
    category_val = category_data.get('category_val') or ''

    if category_val == '':
        await call.answer(text='❗Содержимое категории не указано!',
                          show_alert=True)
        return

    data = await get_wishlist_params(user_id=user_id) or {}
    contact_id = data.get('contact_id')
    first_name = data.get('first_name') or ''
    last_name = data.get('last_name') or ''
    middle_name = data.get('middle_name') or ''
    birthdate = data.get('birthdate') or ''
    categories = data.get('categories') or {}

    categories[category_id] = category_val

    data = {
        'contact_id': contact_id,
        'first_name': first_name,
        'last_name': last_name,
        'middle_name': middle_name,
        'birthdate': birthdate,
        'categories': categories
    }
    await set_wishlist_params(user_id=user_id, data=data)

    message_text = await get_add_wishlist_message_func(user_id=user_id, text_field=text_field)

    categories_on_page = []

    await call.message.edit_text(text=message_text,
                                 reply_markup=await wishlist_creation_keyboard(user_id=user_id,
                                                                               categories_on_page=categories_on_page,
                                                                               wishlist_type=wishlist_type))
    return


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'create_wish'))
async def call_create_wishlist(call: types.CallbackQuery, callback_data: GeneralKb):
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

    data = await get_wishlist_params(user_id=user_id) or {}
    contact_id = data.get('contact_id')
    categories = data.get('categories') or {}

    if len(list(categories.keys())) == 0:
        await call.answer(text='❗Содержимое категории не указано!',
                          show_alert=True)
        return

    data = json.dumps(data)

    await create_record_in_wishlists_sql_query(user_id=user_id,
                                               contact_id=contact_id,
                                               data=data)

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
@router.callback_query(GeneralKb.filter(F.action == 'add_wishlist'))
async def call_select_other_wishlist(call: types.CallbackQuery, callback_data: GeneralKb):
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

    text_field = ('Для изменения параметра, напишите\n'
                  'его в ответ на это сообщение с\n'
                  'указанием нового значения.')

    if wishlist_type == 'other':
        message_text = ('<b>Выбери, для кого ты хочешь\n'
                        'создать новый вишлист.</b>')

        await call.message.edit_text(text=message_text,
                                     reply_markup=await wishlists_other_keyboard(user_id=user_id))

        return
    elif wishlist_type == 'contacts':
        message_text = '👤 <b>Выбери контакта</b>'

        page = 1
        user_contacts_list = await get_user_contacts_list_sql_query(user_id=user_id)

        contacts_on_page = get_contacts_on_page(contacts_list=user_contacts_list, page=page)

        await set_contacts_pagination_page(user_id=user_id, new_page=page)

        await call.message.edit_text(text=message_text,
                                     reply_markup=await wishlist_contacts_list_keyboard(user_id=user_id,
                                                                                        contacts_on_page=contacts_on_page))
        return
    elif wishlist_type == 'me':
        await wishlist_creation_func(user_id=user_id, contact_id=user_id)
        message_text = await get_add_wishlist_message_func(user_id=user_id, text_field=text_field)

        categories_on_page = []

        await call.message.edit_text(text=message_text,
                                     reply_markup=await wishlist_creation_keyboard(user_id=user_id,
                                                                                   categories_on_page=categories_on_page,
                                                                                   wishlist_type=wishlist_type))
        return
    elif wishlist_type == 'contact':
        contact_id = result['contact_id']

        await wishlist_creation_func(user_id=user_id, contact_id=contact_id)
        message_text = await get_add_wishlist_message_func(user_id=user_id, text_field=text_field)

        categories_on_page = []

        await call.message.edit_text(text=message_text,
                                     reply_markup=await wishlist_creation_keyboard(user_id=user_id,
                                                                                   categories_on_page=categories_on_page,
                                                                                   wishlist_type=wishlist_type))
        return
    else:
        contact_id = -1
        await wishlist_creation_func(user_id=user_id, contact_id=contact_id)
        message_text = await get_add_wishlist_message_func(user_id=user_id, text_field=text_field)

        categories_on_page = []

        await call.message.edit_text(text=message_text,
                                     reply_markup=await wishlist_creation_keyboard(user_id=user_id,
                                                                                   categories_on_page=categories_on_page,
                                                                                   wishlist_type=wishlist_type))
        return


async def change_wishlist_params_func(message: types.Message, user_id, wishlist_type):
    user_text = message.text.split()

    error_flag = False

    action_name = user_text[0].lower()
    wishlist_param = user_text[1:]

    wishlist_param = " ".join(wishlist_param)

    data = await get_wishlist_params(user_id=user_id) or {}
    contact_id = data.get('contact_id')
    first_name = data.get('first_name') or ''
    last_name = data.get('last_name') or ''
    middle_name = data.get('middle_name') or ''
    birthdate = data.get('birthdate') or ''
    categories = data.get('categories') or {}

    text_field = ('Для изменения параметра, напишите\n'
                  'его в ответ на это сообщение с\n'
                  'указанием нового значения.')

    if action_name == 'имя':
        if len(wishlist_param) > MAX_WISHLIST_FIRST_NAME_LEN:
            error_flag = True
            text_field = ('❗Введённое имя слишком\n'
                          'длинное. Максимальная длина\n'
                          f'ограничена <b>{MAX_WISHLIST_FIRST_NAME_LEN}</b> символами.\n')

        first_name = wishlist_param.capitalize()

    elif action_name == 'фамилия':
        if len(wishlist_param) > MAX_WISHLIST_LAST_NAME_LEN:
            error_flag = True
            text_field = ('❗Введённая фамилия слишком\n'
                          'длинная. Максимальная длина\n'
                          f'ограничена <b>{MAX_WISHLIST_LAST_NAME_LEN}</b> символами.\n')

        last_name = wishlist_param.capitalize()

    elif action_name == 'отчество':
        if len(wishlist_param) > MAX_WISHLIST_MIDDLE_NAME_LEN:
            error_flag = True
            text_field = ('❗Введённое отчество слишком\n'
                          'длинное. Максимальная длина\n'
                          f'ограничена <b>{MAX_WISHLIST_MIDDLE_NAME_LEN}</b> символами.\n')

        middle_name = wishlist_param.capitalize()

    elif action_name == 'дата':
        DATE_REGEX = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[0-2])\.(19|20)\d{2}$'
        if re.match(DATE_REGEX, wishlist_param) is None:
            error_flag = True
            text_field = ('❗Введённая дата некорректна.\n'
                          'Введите дату в следующем формате:\n'
                          'дд.мм.гггг - где дд: день, мм: месяц,\n'
                          'гггг: год.')

        birthdate = birthdate_to_unix_timestamp(date_str=wishlist_param)

    else:
        error_flag = True
        text_field = ('❗Указана неизвестная команда.\n'
                      'Доступные команды: имя, фамилия,\n'
                      'отчество, дата.')

    if not error_flag:
        data = {
            'contact_id': contact_id,
            'first_name': first_name,
            'last_name': last_name,
            'middle_name': middle_name,
            'birthdate': birthdate,
            'categories': categories
        }
        await set_wishlist_params(user_id=user_id, data=data)

    message_text = await get_add_wishlist_message_func(user_id=user_id, text_field=text_field)

    categories_on_page = []

    try:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message.reply_to_message.message_id,
                                    text=message_text,
                                    reply_markup=await wishlist_creation_keyboard(user_id=user_id,
                                                                                  categories_on_page=categories_on_page,
                                                                                  wishlist_type=wishlist_type))
        await message.delete()
    except Exception as err:
        logger.warning(err)
        return


async def change_wishlist_category_params_func(message: types.Message, user_id, category_id, wishlist_type):
    user_text = message.text
    category_param = user_text
    error_flag = False

    text_field = ('Чтобы указать содержимое категории,\n'
                  f'напишите вашу информацию в ответ на\n'
                  f'это сообщение.')

    if len(category_param) > MAX_WISHLIST_CATEGORY_VAL_LEN:
        error_flag = True
        text_field = ('❗Введёное содержимое категории\n'
                      'слишком длинное. Максимальная\n'
                      f'длина ограничена <b>{MAX_WISHLIST_CATEGORY_VAL_LEN}</b> символами.\n')

    category_val = category_param

    if not error_flag:
        data = {
            'category_val': category_val,
        }
        await set_wishlist_category_params(user_id=user_id, data=data)

    message_text = await get_add_wishlist_category_message_func(user_id=user_id,
                                                                category_id=category_id,
                                                                text_field=text_field)
    try:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message.reply_to_message.message_id,
                                    text=message_text,
                                    reply_markup=await wishlist_add_category_keyboard(user_id=user_id,
                                                                                      category_id=category_id,
                                                                                      wishlist_type=wishlist_type))
        await message.delete()
    except Exception as err:
        logger.warning(err)
        return
