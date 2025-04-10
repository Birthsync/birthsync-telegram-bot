from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from loguru import logger


@logger.catch()
async def main_keyboard():
    builder = ReplyKeyboardBuilder()

    builder.row(
        types.KeyboardButton(text="📅 События"),
        types.KeyboardButton(text="🪄 Вишлисты"),
        types.KeyboardButton(text="🗂 Категории"),
    )
    builder.row(
        types.KeyboardButton(text="👤 Профиль"),
        types.KeyboardButton(text="👥 Контакты"),
        types.KeyboardButton(text="⚙ Настройки"),
    )

    keyboard = builder.as_markup(resize_keyboard=True)
    return keyboard
