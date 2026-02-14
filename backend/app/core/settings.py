import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_file() -> str:
    env = os.getenv("APP_ENV", "development")
    if env == "production":
        return ".env.production"
    if env == "test":
        return ".env.test"
    return ".env.development"


def load_yaml_config() -> dict[str, Any]:
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    if config_path.exists():
        with config_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(), env_file_encoding="utf-8", extra="ignore"
    )

    def __init__(self, **values: Any):
        yaml_config = load_yaml_config()
        # YAML values have lower priority than environment variables
        # but higher priority than class defaults
        combined_values = {**yaml_config, **values}
        super().__init__(**combined_values)

    debug: bool = False
    app_env: str = "development"

    # Database
    db_name: str
    db_user: str
    db_password: SecretStr
    db_host: str
    db_port: int

    # JWT Security
    algorithm: str = "HS256"
    access_token_secret: SecretStr
    refresh_token_secret: SecretStr
    refresh_token_hmac_secret: SecretStr
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # Logging
    logging_hmac_secret: SecretStr
    log_dir: str = "logs"
    log_file_text: str = "app.log"
    log_file_json: str = "app.json.log"

    test_log_dir: str = "test_logs"
    test_log_file_text: str = "test_app.log"
    test_log_file_json: str = "test_app.json.log"

    # CORS
    backend_cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ]

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password.get_secret_value()}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
