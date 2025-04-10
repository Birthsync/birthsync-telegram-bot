from loguru import logger

from src.database.context_manager import db_connection


@logger.catch()
async def get_user_card_info_sql_query(user_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchrow('SELECT first_name, last_name, middle_name, birthdate '
                                        'FROM user_cards '
                                        'WHERE user_id = $1',
                                        user_id)
            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def get_user_first_name_sql_query(user_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchval('SELECT first_name '
                                        'FROM user_cards '
                                        'WHERE user_id = $1',
                                        user_id)
            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def get_user_last_name_sql_query(user_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchval('SELECT last_name '
                                        'FROM user_cards '
                                        'WHERE user_id = $1',
                                        user_id)
            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def get_user_birthdate_sql_query(user_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchval('SELECT birthdate '
                                        'FROM user_cards '
                                        'WHERE user_id = $1',
                                        user_id)
            return res
    except Exception as err:
        logger.warning(err)
        return
