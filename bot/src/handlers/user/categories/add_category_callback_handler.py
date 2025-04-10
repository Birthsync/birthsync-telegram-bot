from aiogram import F
from aiogram import Router, types
from loguru import logger

from loader import bot
from src.database.connection_redis import r_async
from src.database.queries.categories.categories_sql import create_record_in_categories_sql_query, get_category_by_name_sql_query
from src.handlers.user.categories.config import (
    MAX_CATEGORY_DESC_LEN,
    MAX_CATEGORY_NAME_LEN
)
from src.handlers.user.categories.inline import (
    create_category_keyboard,
    categories_list_keyboard
)
from src.handlers.user.categories.redis import (
    get_categories_button_callback,
    get_categories_params,
    set_categories_params,
    remove_categories_params
)
from src.handlers.user.categories.show_categories_handler import show_categories_func
from src.handlers.user.categories.utils import get_categories_message_func
from src.keyboards.config import GeneralKb
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="add_categories")
router.callback_query.middleware(ThrottlingMiddleware(redis_=r_async))


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'create_category'))
async def call_create_category(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)
    result = await get_categories_button_callback(uuid_key=uuid_key)
    if not result:
        try:
            await call.message.delete()
        except Exception as err:
            logger.warning(err)
        return

    user_id = result['user_id']

    data = await get_categories_params(user_id=user_id) or {}
    category_name = data.get('category_name') or ''
    category_desc = data.get('category_desc') or ''

    if (category_name is None) or (category_name == '') or (category_name == ' '):
        await call.answer(text='❗Имя категории не укзаано, либо указано неверно.', show_alert=True)
        return

    if await get_category_by_name_sql_query(user_id=user_id, name=category_name):
        await call.answer(text='❗Такая категория уже создана.', show_alert=True)
        return

    try:
        await create_record_in_categories_sql_query(user_id=user_id,
                                                    name=category_name,
                                                    desc=category_desc)
    except Exception as err:
        logger.warning(err)
        return

    text_message = f'✅ Категория {category_name} успешно создана.'

    try:
        await call.answer(text=text_message, show_alert=True)

        message_text, categories_on_page = await show_categories_func(user_id=user_id)

        await call.message.edit_text(text=message_text,
                                     reply_markup=await categories_list_keyboard(user_id=user_id,
                                                                                 categories_on_page=categories_on_page))
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'show_avail_cat'))
async def call_show_available_categories_menu(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)
    result = await get_categories_button_callback(uuid_key=uuid_key)
    if not result:
        try:
            await call.message.delete()
        except Exception as err:
            logger.warning(err)
        return

    user_id = result['user_id']

    await remove_categories_params(user_id=user_id)

    text_field = ('<i>Чтобы изменить параметр категории,\n'
                  'напишите в ответ на это сообщение\n'
                  'параметр и его значение.</i>\n')

    text_message = await get_categories_message_func(user_id=user_id, text_field=text_field)

    try:
        await call.message.edit_text(text=text_message,
                                     reply_markup=await create_category_keyboard(user_id=user_id))
    except Exception as err:
        logger.warning(err)
        return


async def change_category_params_func(message: types.Message, user_id):
    user_text = message.text.split()

    error_flag = False

    action_name = user_text[0].lower()
    category_param = user_text[1:]

    category_param = " ".join(category_param)

    data = await get_categories_params(user_id=user_id) or {}
    category_name = data.get('category_name') or ''
    category_desc = data.get('category_desc') or ''

    text_field = ('<i>Чтобы изменить параметр категории,\n'
                  'напишите в ответ на это сообщение\n'
                  'параметр и его значение.</i>\n')

    if action_name == 'название':
        if len(category_param) > MAX_CATEGORY_NAME_LEN:
            error_flag = True
            text_field = ('❗Введённое название слишком\n'
                          'длинное. Максимальная длина\n'
                          f'ограничена <b>{MAX_CATEGORY_NAME_LEN}</b> символами.\n')

        category_name = category_param

    elif action_name == 'описание':
        if len(category_param) > MAX_CATEGORY_DESC_LEN:
            error_flag = True
            text_field = ('❗Введённое описание слишком\n'
                          'длинное. Максимальная длина\n'
                          f'ограничена <b>{MAX_CATEGORY_DESC_LEN}</b> символами.\n')

        category_desc = category_param

    else:
        error_flag = True
        text_field = ('❗Указана неизвестная команда.\n'
                      'Доступные команды: название / описание.')

    if not error_flag:
        data = {
            'user_id': user_id,
            'category_name': category_name,
            'category_desc': category_desc
        }
        await set_categories_params(user_id=user_id, data=data)

    text_message = await get_categories_message_func(user_id=user_id, text_field=text_field)

    try:
        await bot.edit_message_text(chat_id=message.chat.id,
                                    message_id=message.reply_to_message.message_id,
                                    text=text_message,
                                    reply_markup=await create_category_keyboard(user_id=user_id))
    except Exception as err:
        logger.warning(err)
        return
