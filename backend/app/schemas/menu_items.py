from datetime import datetime
from decimal import Decimal

from pydantic import Field

from app.schemas.base import Schema, UpdateSchema


class MenuItemCreate(Schema):
    tenant_id: int
    category_id: int
    name: str = Field(max_length=100)
    price: Decimal = Field(max_digits=10, decimal_places=2)
    image_url: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=500)
    sort_order: int = 0
    is_available: bool = True
    is_active: bool = True


class MenuItemUpdate(UpdateSchema):
    non_nullable_fields = frozenset(
        {"category_id", "name", "price", "sort_order", "is_available", "is_active"}
    )

    category_id: int | None = None
    name: str | None = Field(default=None, max_length=100)
    price: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    image_url: str | None = Field(default=None, max_length=500)
    description: str | None = Field(default=None, max_length=500)
    sort_order: int | None = None
    is_available: bool | None = None
    is_active: bool | None = None


class MenuItemRead(MenuItemCreate):
    id: int
    created_at: datetime
