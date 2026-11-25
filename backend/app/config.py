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
    db_ssl_ca_file: Path | None = None
    secret_key: str = ""
    access_token_expire_minutes: int = 60
    rate_limit_storage_url: str = "memory://"
    rate_limit_per_minute: int = Field(default=120, gt=0)
    rate_limit_login_per_minute: int = Field(default=10, gt=0)
    rate_limit_register_per_hour: int = Field(default=5, gt=0)
    serve_frontend: bool = False
    frontend_dist_dir: Path = BASE_DIR.parent / "frontend" / "dist"
    enable_docs: bool = False
    # Comma-separated CIDRs of reverse proxies whose forwarded headers are trusted.
    # Leave empty unless the app sits behind a proxy you control.
    trusted_proxy_ips: str = ""
    frontend_csp: str = (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
        "img-src 'self' https: data:; font-src 'self' data:; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
    )

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
