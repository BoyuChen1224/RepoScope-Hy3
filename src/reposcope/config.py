from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    hy3_base_url: str = "https://tokenhub.tencentmaas.com/v1"
    hy3_api_key: str = "EMPTY"
    hy3_model: str = "hy3"
    hy3_enable_reasoning_effort: bool = False
    hy3_reasoning_effort: str = "high"

    reposcope_max_repo_mb: int = Field(default=80, ge=1, le=500)
    reposcope_clone_timeout_seconds: int = Field(default=90, ge=10, le=600)
    reposcope_allowed_git_hosts: tuple[str, ...] = ("github.com",)

    @field_validator("reposcope_allowed_git_hosts", mode="before")
    @classmethod
    def split_hosts(cls, value: object) -> object:
        if isinstance(value, str):
            return tuple(host.strip().lower() for host in value.split(",") if host.strip())
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()

