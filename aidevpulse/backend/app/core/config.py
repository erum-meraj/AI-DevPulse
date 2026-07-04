from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central app configuration. All values come from environment / .env.
    Never hardcode secrets or environment-specific values elsewhere in the codebase.
    """

    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str

    DATABASE_URL: str
    REDIS_URL: str

    DISCORD_BOT_TOKEN: str | None = None

    TIMEZONE: str = "UTC"
    DAILY_BRIEF_HOUR: int = 7

    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Cached settings accessor. Use as a FastAPI dependency: Depends(get_settings)."""
    return Settings()
