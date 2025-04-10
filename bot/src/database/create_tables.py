from loguru import logger

from src.database.context_manager import db_cursor
from src.database.tables import (
    table_users,
    table_user_cards,
    table_contacts,
    table_wishlists,
    table_user_categories
)


@logger.catch()
async def create_tables_func():
    async with db_cursor() as cursor:
        await cursor.execute(table_users)
        await cursor.execute(table_user_cards)
        await cursor.execute(table_contacts)
        await cursor.execute(table_wishlists)
        await cursor.execute(table_user_categories)

    logger.success('All tables created / loaded.')

