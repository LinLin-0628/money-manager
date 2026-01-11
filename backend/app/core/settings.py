from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    debug: bool = False

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

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_password.get_secret_value()}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
