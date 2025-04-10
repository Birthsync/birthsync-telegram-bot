from __future__ import annotations

import time
from typing import *

import redis.asyncio.client
from aiogram import BaseMiddleware, types
from aiogram.types import Message, CallbackQuery
from loguru import logger
from src.database.connection_redis import r_async as r

import src.messages.system_messages as sm
from config.config_reader import OWNER_ID, BANNED_USERS, settings
import dill

from src.database.queries.general.general_sql import is_user_superuser_sql_query

RATE_LIMIT = settings.RATE_LIMIT
CALLBACK_RATE_LIMIT = settings.CALLBACK_RATE_LIMIT


class ThrottlingMiddlewareCallbackQuery(BaseMiddleware):
    def __init__(self, redis_: redis.asyncio.Redis, limit=CALLBACK_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        self.throttle_manager = ThrottleManager(redis_=redis_)
        super().__init__()

    async def __call__(self, handler, event, data):
        if isinstance(event, CallbackQuery):
            try:
                await self.on_process_callback_event(event)
            except CancelHandler:
                # Cancel current handler
                return
        return await handler(event, data)

    async def on_process_callback_event(self, query: CallbackQuery):
        limit = self.rate_limit
        key = f"{self.prefix}_callback_query"

        try:
            if query.from_user.id in BANNED_USERS:
                raise CancelHandler()
            if query.from_user.id == OWNER_ID:
                return
            await self.throttle_manager.throttle_callback(key, rate=limit, user_id=query.from_user.id)
        except Throttled:
            await query.answer(text=sm.throttling_callback_msg)
            logger.warning(f'{query.from_user.id} - callback flood.')
            raise CancelHandler()


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, redis_: redis.asyncio.Redis, limit=RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        self.throttle_manager = ThrottleManager(redis_=redis_)

        super(ThrottlingMiddleware, self).__init__()

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        try:
            await self.on_process_event(event)
        except CancelHandler:
            # Cancel current handler
            return

        try:
            result = await handler(event, data)
        except Exception as e:
            print(e)
            return

        return result

    async def on_process_event(self, event: Message) -> Any:
        limit = self.rate_limit
        key = f"{self.prefix}_message"

        # Use ThrottleManager.throttle method.
        try:
            user_id = event.from_user.id

            res = await is_user_superuser_sql_query(user_id=user_id)
            if (res is not None) and (not res):
                raise CancelHandler()

            if isinstance(event, types.CallbackQuery):
                user_id = event.from_user.id

                await self.throttle_manager.throttle_callback(key, rate=limit, user_id=event.from_user.id)
            else:
                chat_id = event.chat.id
                user_id = event.from_user.id
                active_key = f'{user_id}_activity'
                active_val = 'active'
                not_active_val = 'not_active'

                # cached_value = await r_async.get(active_key)
                # if cached_value:
                #     val = dill.loads(cached_value)
                #     if val == not_active_val:
                #         raise CancelHandler()
                # else:
                #     pass
                # async with async_session_factory() as session:
                #     if not await get_is_active(session=session, user_id=user_id):
                #         r.set(active_key, dill.dumps(not_active_val), ex=10)
                #         raise CancelHandler()
                #     else:
                #         r.set(active_key, dill.dumps(active_val), ex=10)

                # async with async_session_factory() as session:
                #     if not await chat_user_exists(session=session, chat_id=chat_id, user_id=user_id):
                #         await add_new_user_chat(event=event)

                await self.throttle_manager.throttle(key, rate=limit, user_id=event.from_user.id, chat_id=event.chat.id)
        except Throttled:
            # Execute action
            # await self.event_throttled(event, t)
            # Cancel current handler
            if isinstance(event, types.CallbackQuery):
                await event.answer(text=sm.throttling_callback_msg)
            logger.warning(f'{event.from_user.id} - message flood.')
            raise CancelHandler()

    # async def event_throttled(self, event: Message, throttled: Throttled):
    #     # Calculate how manytime is left till the block ends
    #     delta = throttled.rate - throttled.delta
    #     # Prevent flooding
    #     if throttled.exceeded_count <= 2:
    #         await event.answer(f'Too many requests.\nTry again in {delta:.2f} seconds.')


class ThrottleManager:
    bucket_keys = [
        "RATE_LIMIT", "DELTA",
        "LAST_CALL", "EXCEEDED_COUNT"
    ]

    def __init__(self, redis_: redis.asyncio.Redis):
        self.redis = redis_

    async def throttle(self, key: str, rate: float, user_id: int, chat_id: int):
        now = time.time()
        bucket_name = f'throttle_{key}_{user_id}_{chat_id}'

        data = await self.redis.hmget(bucket_name, self.bucket_keys)
        data = {
            k: float(v.decode())
            if isinstance(v, bytes)
            else v
            for k, v in zip(self.bucket_keys, data)
            if v is not None
        }
        # Calculate
        called = data.get("LAST_CALL", now)
        delta = now - float(called)
        result = delta >= rate or delta <= 0
        # Save result
        data["RATE_LIMIT"] = rate
        data["LAST_CALL"] = now
        data["DELTA"] = delta
        if not result:
            data["EXCEEDED_COUNT"] = int(data["EXCEEDED_COUNT"])
            data["EXCEEDED_COUNT"] += 1
        else:
            data["EXCEEDED_COUNT"] = 1

        await self.redis.hset(bucket_name, mapping=data)

        if not result:
            raise Throttled(key=key, chat=chat_id, user=user_id, **data)
        return result

    async def throttle_callback(self, key: str, rate: float, user_id: int):
        now = time.time()
        bucket_name = f'throttle_{key}_{user_id}'

        data = await self.redis.hmget(bucket_name, self.bucket_keys)
        data = {
            k: float(v.decode())
            if isinstance(v, bytes)
            else v
            for k, v in zip(self.bucket_keys, data)
            if v is not None
        }
        # Calculate
        called = data.get("LAST_CALL", now)
        delta = now - float(called)
        result = delta >= rate or delta <= 0
        # Save result
        data["RATE_LIMIT"] = rate
        data["LAST_CALL"] = now
        data["DELTA"] = delta
        if not result:
            data["EXCEEDED_COUNT"] = int(data["EXCEEDED_COUNT"])
            data["EXCEEDED_COUNT"] += 1
        else:
            data["EXCEEDED_COUNT"] = 1

        await self.redis.hset(bucket_name, mapping=data)

        if not result:
            raise Throttled(key=key, user=user_id, **data)
        return result


class Throttled(Exception):
    def __init__(self, **kwargs):
        self.key = kwargs.pop("key", '<None>')
        self.called_at = kwargs.pop("LAST_CALL", time.time())
        self.rate = kwargs.pop("RATE_LIMIT", None)
        self.exceeded_count = kwargs.pop("EXCEEDED_COUNT", 0)
        self.delta = kwargs.pop("DELTA", 0)
        self.user = kwargs.pop('user', None)
        self.chat = kwargs.pop('chat', None)

    def __str__(self):
        return f"Rate limit exceeded! (Limit: {self.rate} s, " \
               f"exceeded: {self.exceeded_count}, " \
               f"time delta: {round(self.delta, 3)} s)"


class CancelHandler(Exception):
    pass
