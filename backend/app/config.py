from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str = "qr_menu"
    db_user: str
    db_password: str
    db_ssl_enabled: bool = False
    db_ssl_ca_pem: str = ""
    secret_key: str = ""
    access_token_expire_minutes: int = 60
    rate_limit_storage_url: str = "memory://"
    rate_limit_per_minute: int = Field(default=120, gt=0)
    rate_limit_login_per_minute: int = Field(default=10, gt=0)
    rate_limit_register_per_hour: int = Field(default=5, gt=0)
    serve_frontend: bool = False
    frontend_dist_dir: Path = BASE_DIR.parent / "frontend" / "dist"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
