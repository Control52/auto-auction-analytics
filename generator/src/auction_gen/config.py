"""Настройки генератора: читаются из переменных окружения и файла .env.
"""

from dataclasses import dataclass

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ClickHouseSettings(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="CLICKHOUSE_", env_file=".env", extra="ignore")

    host: str = "localhost"
    port: int = Field(default=8123, ge=1, le=65535)
    database: str = "auctions"
    user: str = "default"
    password: str = ""


class GeneratorSettings(BaseSettings):

    model_config = SettingsConfigDict(env_prefix="GENERATOR_", env_file=".env", extra="ignore")

    interval_seconds: float = Field(default=1.0, gt=0)
    lots_at_peak: int = Field(default=100, ge=1)
    seed: int = 42
    anomaly_probability: float = Field(default=0.02, ge=0, le=1)

    log_level: str = "INFO"

    retry_max_attempts: int = Field(default=5, ge=1)
    retry_base_delay_seconds: float = Field(default=0.5, ge=0)
    retry_max_delay_seconds: float = Field(default=30.0, ge=0)
    retry_backoff_factor: float = Field(default=2.0, ge=1)


@dataclass(frozen=True, slots=True)
class Settings:

    generator: GeneratorSettings
    clickhouse: ClickHouseSettings


def get_settings() -> Settings:
    return Settings(generator=GeneratorSettings(), clickhouse=ClickHouseSettings())
