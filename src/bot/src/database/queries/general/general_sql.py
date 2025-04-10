from loguru import logger

from src.database.context_manager import db_connection


@logger.catch()
async def get_user_exists_sql_query(user_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchval('SELECT COUNT(1) '
                                        'FROM users '
                                        'WHERE user_id = $1',
                                        user_id)
            return True if res == 0 else False
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def is_user_superuser_sql_query(user_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchval('SELECT is_superuser '
                                        'FROM users '
                                        'WHERE user_id = $1',
                                        user_id)
            return res
    except Exception as err:
        logger.warning(err)
        return
