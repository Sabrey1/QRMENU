from datetime import datetime

from pydantic import Field

from app.schemas.base import Schema, UpdateSchema


class BannerCreate(Schema):
    image_url: str = Field(min_length=1, max_length=500, pattern=r"^https?://\S+$")
    alt_text: str = Field(default="", max_length=200)
    sort_order: int = 0
    is_active: bool = True


class BannerUpdate(UpdateSchema):
    non_nullable_fields = frozenset({"image_url", "alt_text", "sort_order", "is_active"})

    image_url: str | None = Field(default=None, min_length=1, max_length=500, pattern=r"^https?://\S+$")
    alt_text: str | None = Field(default=None, max_length=200)
    sort_order: int | None = None
    is_active: bool | None = None


class BannerRead(BannerCreate):
    id: int
    tenant_id: int
    created_at: datetime
