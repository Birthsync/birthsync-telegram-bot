from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties

from config.config_reader import settings


bot = Bot(token=settings.BOT_TOKEN.get_secret_value(),
          default=DefaultBotProperties(parse_mode='html'))
dp = Dispatcher(bot=bot)
