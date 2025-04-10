from loguru import logger

from src.database.context_manager import db_connection


@logger.catch()
async def get_user_categories_list_sql_query(user_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetch('SELECT id '
                                     'FROM user_categories '
                                     'WHERE user_id = $1',
                                     user_id)
            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def get_category_name_sql_query(category_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchval('SELECT name '
                                        'FROM user_categories '
                                        'WHERE id = $1',
                                        category_id)
            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def get_category_desc_sql_query(category_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchval('SELECT description '
                                        'FROM user_categories '
                                        'WHERE id = $1',
                                        category_id)
            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def get_category_by_name_sql_query(user_id, name):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchval('SELECT id '
                                        'FROM user_categories '
                                        'WHERE user_id = $1 AND name = $2',
                                        user_id, name)
            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def create_record_in_categories_sql_query(user_id, name, desc=None):
    try:
        async with db_connection() as cursor:
            res = await cursor.execute('INSERT INTO user_categories(user_id, name, description) '
                                       'VALUES($1, $2, $3)',
                                       user_id, name, desc)
            return res
    except Exception as err:
        logger.warning(err)
        return
