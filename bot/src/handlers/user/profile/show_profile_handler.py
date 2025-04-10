from aiogram import Router, types, F
from loguru import logger

from src.database.connection_redis import r_async
from src.handlers.user.profile.inline import profile_keyboard
from src.handlers.user.profile.utils import get_profile_message_func
from src.middlewares.throttling import ThrottlingMiddleware

router = Router(name="show_profile")
router.message.middleware(ThrottlingMiddleware(redis_=r_async))


@router.message(F.text.lower().in_({'профиль', '👤 профиль'}))
async def show_profie_cmd(message: types.Message):
    user_id: int = message.from_user.id

    message_text = await get_profile_message_func(user_id=user_id)

    await message.answer(text=message_text,
                         reply_markup=await profile_keyboard(user_id=user_id))
    # await message.answer(text=str(message))

    logger.debug(f'{user_id} -> отобразил свой профиль.')
