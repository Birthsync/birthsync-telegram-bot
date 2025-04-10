from loguru import logger

from src.handlers.user.categories.config import MAX_CATEGORIES_BUTTONS_ON_PAGE
from src.handlers.user.categories.redis import get_categories_params


@logger.catch()
def get_categories_on_page(categories_list, page):
    start_index = (page - 1) * MAX_CATEGORIES_BUTTONS_ON_PAGE
    end_index = start_index + MAX_CATEGORIES_BUTTONS_ON_PAGE
    categories_on_page = categories_list[start_index:end_index]
    return categories_on_page


async def get_categories_message_func(user_id, text_field):
    data = await get_categories_params(user_id=user_id) or {}
    category_name = data.get('category_name') or ''
    category_desc = data.get('category_desc') or ''

    text_message = ('🗂 <b>Создание категории</b>\n'
                    '<code>················</code>\n'
                    f'<b>Название:</b> {category_name}\n'
                    f'<b>Описание:</b> {category_desc}\n'
                    '<code>················</code>\n'
                    f'{text_field}'
                    '<code>················</code>\n'
                    '<blockquote>Пример 1:  <code>название Еда</code>\n'
                    'Пример 2:  <code>описание Любимая еда</code></blockquote>')

    return text_message
