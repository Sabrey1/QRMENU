from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_categories_tenant_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(server_default="0")
    is_active: Mapped[bool] = mapped_column(server_default="1")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())