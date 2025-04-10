from loguru import logger

from src.database.context_manager import db_connection


@logger.catch()
async def get_user_wishlists_list_sql_query(user_id, contact_id):
    try:
        async with db_connection() as cursor:
            if user_id == contact_id:
                res = await cursor.fetch('SELECT id '
                                         'FROM wishlists '
                                         'WHERE user_id = $1 AND contact_id = $2',
                                         user_id, contact_id)
            else:
                res = await cursor.fetch('SELECT id '
                                         'FROM wishlists '
                                         'WHERE user_id = $1 '
                                         'AND contact_id != $2',
                                         user_id, user_id)

            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def get_user_wishlist_data_sql_query(user_id, wishlist_id):
    try:
        async with db_connection() as cursor:
            res = await cursor.fetchval('SELECT data '
                                        'FROM wishlists '
                                        'WHERE user_id = $1 AND id = $2',
                                        user_id, wishlist_id)
            return res
    except Exception as err:
        logger.warning(err)
        return


@logger.catch()
async def create_record_in_wishlists_sql_query(user_id, contact_id, data):
    try:
        async with db_connection() as cursor:
            await cursor.execute('INSERT INTO wishlists(user_id, contact_id, data) '
                                 'VALUES($1, $2, $3)',
                                 user_id, contact_id, data)
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
