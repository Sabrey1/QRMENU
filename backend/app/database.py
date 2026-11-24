from collections.abc import Iterator
import ssl

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import BASE_DIR, settings

database_url = URL.create(
    drivername="mysql+pymysql",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
    query={"charset": "utf8mb4"},
)

def build_connect_args(config):
    ca_file = config.db_ssl_ca_file
    ca_pem = config.db_ssl_ca_pem
    if ca_file and ca_pem:
        raise ValueError("Use either DB_SSL_CA_FILE or DB_SSL_CA_PEM, not both")
    if not config.db_ssl_enabled:
        if ca_file or ca_pem:
            raise ValueError("Set DB_SSL_ENABLED=true when configuring a database CA certificate")
        return {}
    if ca_file and not ca_file.is_absolute():
        ca_file = BASE_DIR / ca_file
    context = ssl.create_default_context(cafile=str(ca_file) if ca_file else None, cadata=ca_pem or None)
    return {"ssl": context}


engine = create_engine(database_url, pool_pre_ping=True, connect_args=build_connect_args(settings))
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    with SessionLocal() as session:
        yield session
