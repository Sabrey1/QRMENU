from datetime import datetime

import re

from pydantic import Field, computed_field

from app.schemas.base import Schema, UpdateSchema


class TenantCreate(Schema):
    name: str = Field(max_length=100)
    slug: str | None = Field(default=None, max_length=500)
    logo_url: str | None = Field(default=None, max_length=500)
    currency_code: str = Field(max_length=3)
    display_template: str = Field(default="default_template", min_length=1, max_length=100, pattern=r"^[a-z0-9_]+$")
    is_published: bool = True


class TenantUpdate(UpdateSchema):
    non_nullable_fields = frozenset({"name", "currency_code", "display_template", "is_published"})

    name: str | None = Field(default=None, max_length=100)
    slug: str | None = Field(default=None, max_length=500)
    logo_url: str | None = Field(default=None, max_length=500)
    currency_code: str | None = Field(default=None, max_length=3)
    display_template: str | None = Field(default=None, min_length=1, max_length=100, pattern=r"^[a-z0-9_]+$")
    is_published: bool | None = None


class TenantRead(TenantCreate):
    id: int
    trial_started_at: datetime
    trial_ends_at: datetime
    paid_until: datetime
    created_at: datetime

    @computed_field
    @property
    def menu_url(self) -> str | None:
        if not self.slug or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", self.slug):
            return None
        return f"https://{self.slug}.sabrey.xyz"
