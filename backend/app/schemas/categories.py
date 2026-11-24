from datetime import datetime

from pydantic import Field

from app.schemas.base import Schema, UpdateSchema


class CategoryCreate(Schema):
    tenant_id: int
    name: str = Field(max_length=100)
    description: str | None = Field(default=None, max_length=500)
    sort_order: int = 0
    is_active: bool = True


class CategoryUpdate(UpdateSchema):
    non_nullable_fields = frozenset({"name", "sort_order", "is_active"})

    name: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryRead(CategoryCreate):
    id: int
    created_at: datetime
