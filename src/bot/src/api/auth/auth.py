from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.connection import get_async_session
from src.database.queries.auth.auth import (
    get_user_by_phone_query,
    create_new_user_query
)
from src.services.auth import create_access_token, create_refresh_token
from src.database.schemas import UserCreate, UserAuth, Token

router = APIRouter()


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_async_session)):
    existing_user = await get_user_by_phone_query(db, user_data.phone_number)
    if existing_user:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")

    user = await create_new_user_query(db, user_data.phone_number)

    access_token = create_access_token({"sub": user.phone_number})
    refresh_token = create_refresh_token({"sub": user.phone_number})

    return {"access_token": access_token, "refresh_token": refresh_token}


@router.post("/login", response_model=Token)
async def login(user_auth: UserAuth, db: AsyncSession = Depends(get_async_session)):
    user = await get_user_by_phone_query(db, user_auth.phone_number)

    if not user:
        raise HTTPException(status_code=400, detail="Пользователь не найден")

    if user_auth.code != "1234":
        raise HTTPException(status_code=400, detail="Неверный код")

    access_token = create_access_token({"sub": user.phone_number})
    refresh_token = create_refresh_token({"sub": user.phone_number})

    return {"access_token": access_token, "refresh_token": refresh_token}
