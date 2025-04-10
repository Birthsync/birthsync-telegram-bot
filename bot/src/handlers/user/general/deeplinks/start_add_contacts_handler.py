import re

from aiogram import Router, types, F
from aiogram.filters import CommandStart, CommandObject
from loguru import logger

from src.database.connection_redis import r_async
from src.database.queries.contacts.contacts_sql import get_user_contact_sql_query
from src.database.queries.general.general_sql import get_user_exists_sql_query
from src.database.queries.general.register_user_sql import register_new_user_transaction_sql_query
from src.database.queries.user_card.user_card_sql import get_user_first_name_sql_query
from src.handlers.user.general.inline import add_contact_keyboard
from src.keyboards.general_kb import main_keyboard
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="start_add_contact")
router.message.middleware(ThrottlingMiddleware(redis_=r_async))


@router.message(CommandStart(deep_link=True,
                             magic=F.args.regexp(re.compile(r'add_(\d+)'))))
async def start_add_contact_cmd(message: types.Message,
                                command: CommandObject):
    contact_id: int = message.from_user.id

    if await get_user_exists_sql_query(user_id=contact_id):
        if message.chat.type == 'private':
            await register_new_user_transaction_sql_query(message=message)
            return

    args = command.args.split('_')
    user_id = int(args[1])

    if user_id == contact_id:
        await message.answer(text='❗Самого себя добавить в контакты нельзя!')
        return

    user_firstname = await get_user_first_name_sql_query(user_id=user_id)
    contact_firstname = await get_user_first_name_sql_query(user_id=contact_id)

    if await get_user_contact_sql_query(user_id=user_id, contact_id=contact_id):
        await message.answer(text=f'❗Пользователь <b>{user_firstname}</b> уже находится в вашем списке контактов!')
        return

    await message.answer(text=f'Юзер {user_firstname} хочет добавить тебя в свои контакты!',
                         reply_markup=await main_keyboard())

    await message.answer(text=f'<b>Добавить {user_firstname} в контакты?</b>\n'
                              f'<blockquote>Внимание!\n'
                              f'Пользователь получит информацию\n'
                              f'о вашем аккаунте, а именно:\n'
                              f'- ФИО\n'
                              f'- Дата рождения\n'
                              f'</blockquote>',
                         reply_markup=await add_contact_keyboard(user_id=user_id,
                                                                 contact_id=contact_id))

    logger.debug(f'{contact_id} -> использовал /start_add')
