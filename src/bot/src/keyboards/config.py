from aiogram.filters.callback_data import CallbackData

CALLBACK_LIFETIME = 3600


class GeneralKb(CallbackData, prefix="general"):
    action: str
    uuid_key: str
