from aiogram import Router, types, F
from loguru import logger

from src.database.connection_redis import r_async
from src.database.queries.contacts.contacts_sql import get_user_contacts_list_sql_query
from src.handlers.user.contacts.inline import contacts_list_keyboard
from src.handlers.user.contacts.redis import set_contacts_pagination_page
from src.handlers.user.contacts.utils import get_contacts_on_page
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="contacts")
router.message.middleware(ThrottlingMiddleware(redis_=r_async))


@router.message(F.text.lower().in_({'контакты', '👥 контакты'}))
async def show_contacts_cmd(message: types.Message):
    user_id: int = message.from_user.id

    message_text = '👥 <b>Твои контакты</b>'

    page = 1
    user_contacts_list = await get_user_contacts_list_sql_query(user_id=user_id)

    contacts_on_page = get_contacts_on_page(contacts_list=user_contacts_list, page=page)

    await set_contacts_pagination_page(user_id=user_id, new_page=page)

    await message.answer(text=message_text,
                         reply_markup=await contacts_list_keyboard(user_id=user_id,
                                                                   contacts_on_page=contacts_on_page))

    logger.debug(f'{user_id} -> использовал /start')
