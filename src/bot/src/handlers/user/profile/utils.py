from src.database.queries.user_card.user_card_sql import get_user_card_info_sql_query


async def get_profile_message_func(user_id):

    result = await get_user_card_info_sql_query(user_id=user_id)
    if result is None:
        return

    user_first_name = result[0] or '-'
    user_last_name = result[1] or '-'
    user_middle_name = result[2] or '-'
    user_birthdate = result[3] or '-'

    message_text = ('👤 <b>Профиль</b>\n'
                    '<code>················</code>\n'
                    f'<b>Имя:</b> <i>{user_first_name}</i>\n'
                    f'<b>Фамилия:</b> <i>{user_last_name}</i>\n'
                    f'<b>Отчество:</b> <i>{user_middle_name}</i>\n\n'
                    f'<b>Дата рождения:</b> <i>{user_birthdate}</i>\n')

    return message_text


