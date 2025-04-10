import asyncio

import uvicorn
from fastapi import FastAPI, Request, APIRouter, Response, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api.auth.auth import get_jwt_strategy, cookie_transport
from src.api.auth.manager import get_user_manager, UserManager
from src.api.auth.schemas import UserCreate
from src.api.endpoints.main import router as main_router
from src.api.endpoints.messages import router as msg_router
from src.api.endpoints.users import router as users_router
from src.tcp.server import run_server_TCP

app = FastAPI(
    title="TCP chat-server & client API",
    description="This API provides various POST and GET methods for working with the database and project logic.",
    version="0.1.0",
    terms_of_service="http://example.com/terms/",
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
    contact={
        "telegram": "akulovroma"
    }
)

app.include_router(
    main_router,
    tags=["main"]
)

app.include_router(
    users_router,
    tags=["user"]
)

auth_router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@auth_router.post("/auth/login")
async def login(
        response: Response,
        credentials: LoginRequest,
        user_manager: UserManager = Depends(get_user_manager),
):
    user = await user_manager.authenticate(credentials)
    if user is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    jwt_strategy = get_jwt_strategy()
    token = await jwt_strategy.write_token(user)

    response.set_cookie(
        key=cookie_transport.cookie_name,
        value=token,
        max_age=cookie_transport.cookie_max_age,
        httponly=True,
        secure=True,
    )

    return {"message": "Login successful",
            "user_id": user.id,
            "token": token}


@auth_router.post("/auth/register")
async def register(user_create: UserCreate, user_manager: UserManager = Depends(get_user_manager)):
    try:
        user = await user_manager.create(user_create)
        return {"message": "Registration successful", "user_id": user.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


app.include_router(auth_router, tags=["auth"])

app.include_router(
    msg_router,
    tags=["messages"]
)

origins = [
    "http://localhost",
    "http://localhost:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=["Content-Type", "Set-Cookie", "Access-Control-Allow-Headers", "Access-Control-Allow-Origin",
                   "Authorization"]
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response


async def run_server():
    tcp_task = asyncio.create_task(run_server_TCP())
    config = uvicorn.Config(app, host="127.0.0.1", port=8000)
    server = uvicorn.Server(config)
    fastapi_task = asyncio.create_task(server.serve())

    await asyncio.gather(tcp_task, fastapi_task)
