"""Settings loaded from environment variables / the local `.env` file.

Passwords are `SecretStr`: they never appear in repr(), logs or error messages.
"""

from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=REPO_ROOT / ".env", env_file_encoding="utf-8", extra="ignore")

    meridian_env: str = "development"
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "meridian_dev"
    db_owner_user: str = "meridian_owner"
    db_owner_password: SecretStr = SecretStr("")
    db_reader_user: str = "meridian_reader"
    db_reader_password: SecretStr = SecretStr("")
    test_db_name: str = "meridian_test"
    test_db_user: str = "meridian_test"
    test_db_password: SecretStr = SecretStr("")
    db_connect_timeout_seconds: int = 10
    db_pool_size: int = 5
    olist_raw_dir: Path = Path("data/raw/olist")
    source_timezone: str = "America/Sao_Paulo"
    log_level: str = "INFO"

    @property
    def raw_dir(self) -> Path:
        return self.olist_raw_dir if self.olist_raw_dir.is_absolute() else REPO_ROOT / self.olist_raw_dir


@lru_cache
def get_settings() -> Settings:
    return Settings()
