"""Application configuration loaded from environment."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the Prompt Reverse Engineer service."""

    app_name: str = "Prompt Reverse Engineer"
    app_env: str = "development"
    log_level: str = "INFO"
    host: str = "0.0.0.0"
    port: int = 8000

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", alias="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    model_name: str = Field(default="heuristic-v1", alias="MODEL_NAME")
    temperature_override: float | None = Field(default=None, alias="TEMPERATURE_OVERRIDE")

    max_input_chars: int = 12000
    max_batch_items: int = 20
    max_requests_per_minute: int = 120
    max_unique_texts_per_minute: int = 80
    cache_ttl_seconds: int = 600
    cache_max_entries: int = 2048

    deterministic_default: bool = True
    reproducibility_seed: int = 1337

    injection_keywords_threshold: int = 2

    # Marketplace quota / billing hooks
    per_user_quota_per_minute: int = 120
    per_key_quota_per_minute: int = 180
    billing_unit_chars: int = 1000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""

    return Settings()
