from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from loguru import logger

OWNER_ID = 435918797
ADMINS_LIST = (435918797,)

BANNED_USERS = ()


class EnvBaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


class DBSettings(EnvBaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class CacheSettings(EnvBaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASS: str | None = None
    REDIS_DB: int


class GigaChainSettings(EnvBaseSettings):
    CREDENTIALS: str


class BotSettings(EnvBaseSettings):
    BOT_TOKEN: SecretStr
    RATE_LIMIT: int | float = 1  # for throttling control
    CALLBACK_RATE_LIMIT: int | float = 1  # for callback throttling control
    CALLBACK_LIFETIME: int = 3600
    REDIS_RECORD_LIFETIME: int = 3600


class Settings(BotSettings, DBSettings, CacheSettings, GigaChainSettings):
    DEBUG: bool = False


settings = Settings()
