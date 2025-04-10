from loguru import logger

from src.handlers.user.contacts.config import MAX_CONTACTS_BUTTONS_ON_PAGE


@logger.catch()
def get_contacts_on_page(contacts_list, page):
    start_index = (page - 1) * MAX_CONTACTS_BUTTONS_ON_PAGE
    end_index = start_index + MAX_CONTACTS_BUTTONS_ON_PAGE
    contacts_on_page = contacts_list[start_index:end_index]
    return contacts_on_page
