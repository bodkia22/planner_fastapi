from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    anthropic_api_key: str
    cors_origins: list[str]

    cookie_secure: bool
    cookie_samesite: Literal["lax", "strict", "none"]

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
