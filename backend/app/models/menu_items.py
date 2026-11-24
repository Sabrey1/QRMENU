from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Menu_Items(Base):
    __tablename__ = "menu_items"
    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_menu_item_tenant_name"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    tenant_id: Mapped[int] = mapped_column(ForeignKey("tenants.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    name: Mapped[str] = mapped_column(String(100))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(server_default="0")
    is_available: Mapped[bool] = mapped_column(server_default="1")
    is_active: Mapped[bool] = mapped_column(server_default="1")
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
