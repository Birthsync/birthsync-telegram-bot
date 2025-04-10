from aiogram import F
from aiogram import Router, types
from loguru import logger

from loader import bot
from src.database.connection_redis import r_async
from src.database.queries.contacts.contacts_sql import create_record_in_contacts_sql_query, get_user_contact_sql_query
from src.database.queries.user_card.user_card_sql import get_user_first_name_sql_query
from src.handlers.user.contacts.redis import get_contacts_button_callback
from src.keyboards.config import GeneralKb
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="add_contact")
router.callback_query.middleware(ThrottlingMiddleware(redis_=r_async))


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'add_contact_accept'))
async def call_add_contact_accept(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)
    result = await get_contacts_button_callback(uuid_key=uuid_key)
    if not result:
        try:
            await call.message.delete()
        except Exception as err:
            logger.warning(err)
        return

    user_id = result['user_id']
    contact_id = result['contact_id']

    user_firstname = await get_user_first_name_sql_query(user_id=user_id)
    contact_firstname = await get_user_first_name_sql_query(user_id=contact_id)

    if await get_user_contact_sql_query(user_id=contact_id, contact_id=user_id):
        await call.answer(text=f'❗Пользователь {user_firstname} уже находится в вашем списке контактов!',
                          show_alert=True)
        return

    try:
        await create_record_in_contacts_sql_query(user_id=user_id, contact_id=contact_id)
        await create_record_in_contacts_sql_query(user_id=contact_id, contact_id=user_id)
    except Exception as err:
        logger.warning(err)
        return

    try:
        await call.message.edit_text(text=f'✅ Вы добавили <b>{user_firstname}</b> в список контактов!')

        await bot.send_message(chat_id=user_id,
                               text=f'✔👤 Пользователь <b>{contact_firstname}</b> принял ваш запрос на добавление в контакты.')
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
@router.callback_query(GeneralKb.filter(F.action == 'add_contact_reject'))
async def call_add_contact_reject(call: types.CallbackQuery, callback_data: GeneralKb):
    uuid_key = str(callback_data.uuid_key)
    result = await get_contacts_button_callback(uuid_key=uuid_key)
    if not result:
        try:
            await call.message.delete()
        except Exception as err:
            logger.warning(err)
        return

    user_id = result['user_id']
    contact_id = result['contact_id']

    user_firstname = await get_user_first_name_sql_query(user_id=user_id)
    contact_firstname = await get_user_first_name_sql_query(user_id=contact_id)

    if await get_user_contact_sql_query(user_id=contact_id, contact_id=user_id):
        await call.answer(text=f'❗Пользователь {user_firstname} уже находится в вашем списке контактов!',
                          show_alert=True)
        return

    try:
        await call.message.edit_text(text=f'❌ Вы отклонили запрос <b>{user_firstname}</b>!')

        await bot.send_message(chat_id=user_id,
                               text=f'🚫👤 Пользователь <b>{contact_firstname}</b> отклонил ваш запрос на добавление в контакты.')
    except Exception as err:
        logger.warning(err)
        return
