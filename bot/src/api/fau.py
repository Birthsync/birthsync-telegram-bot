from src.database import User
from fastapi_users import FastAPIUsers
from src.api.auth.manager import get_user_manager
from src.api.auth.auth import auth_backend


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)
