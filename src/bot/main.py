import asyncio
from loguru import logger
from loader import bot, dp
from src.handlers import get_handlers_router
from src.database.create_tables import create_tables_func


async def on_startup() -> None:
    logger.info("bot starting...")

    await bot.delete_webhook(drop_pending_updates=True)

    await create_tables_func()

    dp.include_router(get_handlers_router())

    bot_info = await bot.get_me()

    logger.info(f"Name         - {bot_info.full_name}")
    logger.info(f"Username     - @{bot_info.username}")
    logger.info(f"ID           - {bot_info.id}")

    states: dict[bool | None, str] = {
        True: "Enabled",
        False: "Disabled",
        None: "Unknown (This's not a bot)",
    }

    logger.info(f"Groups Mode  - {states[bot_info.can_join_groups]}")
    logger.info(f"Privacy Mode - {states[not bot_info.can_read_all_group_messages]}")
    logger.info(f"Inline Mode  - {states[bot_info.supports_inline_queries]}")

    logger.info("bot started")


async def on_shutdown() -> None:
    logger.info("bot stopping...")

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.session.close()
    logger.info("bot stopped")


async def main() -> None:
    logger.add(
        "logs/debug.log",
        level="DEBUG",
        format="{time} | {level} | {module}:{function}:{line} | {message}",
        rotation="00:00",
        compression="zip",
    )

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    await dp.start_polling(bot,
                           allowed_updates=["message",
                                            "inline_query",
                                            "chat_member",
                                            "my_chat_member",
                                            "callback_query"])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning(f'bot stopped by KeyboardInterrupt.')
