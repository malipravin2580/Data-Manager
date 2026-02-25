from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Data Manager"
    DEBUG: bool = False

    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30 * 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: str = "postgresql+psycopg2://datamanager:datamanager@postgres:5432/datamanager"
    REDIS_URL: str = "redis://redis:6379/0"

    DATA_DIR: Path = Path("./data")
    MAX_FILE_SIZE: int = 100 * 1024 * 1024

    SHARE_LINK_EXPIRE_DAYS: int = 7
    SHARE_LINK_SALT: str = "share-salt-change-in-production"
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
