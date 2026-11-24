from datetime import datetime

from sqlalchemy import String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    slug: Mapped[str | None] = mapped_column(String(500), unique=True)
    logo_url: Mapped[str | None] = mapped_column(String(500))
    currency_code: Mapped[str] = mapped_column(String(3))
    display_template: Mapped[str] = mapped_column(String(100), default="default_template", server_default="default_template")
    is_published: Mapped[bool] = mapped_column(server_default="1")
    trial_started_at: Mapped[datetime] = mapped_column(server_default=func.now())
    trial_ends_at: Mapped[datetime] = mapped_column(server_default=func.now())
    paid_until: Mapped[datetime] = mapped_column(server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
