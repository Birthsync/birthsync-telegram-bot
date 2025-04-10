from loguru import logger

from src.database.context_manager import db_connection


@logger.catch()
async def get_user_contacts_list_sql_query(user_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetch('SELECT contact_id '
                                     'FROM contacts '
                                     'WHERE user_id = $1 AND contact_id != $2',
                                     user_id, user_id)
            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def get_user_contact_sql_query(user_id, contact_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchrow('SELECT 1 '
                                        'FROM contacts '
                                        'WHERE user_id = $1 AND contact_id = $2',
                                        user_id, contact_id)
            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def create_record_in_contacts_sql_query(user_id, contact_id):
    try:
        async with db_connection() as cursor:
            await cursor.execute('INSERT INTO contacts(user_id, contact_id) '
                                 'VALUES ($1, $2) '
                                 'ON CONFLICT (user_id, contact_id) Do NOTHING',
                                 user_id, contact_id)
    except Exception as err:
        logger.warning(err)
        return
