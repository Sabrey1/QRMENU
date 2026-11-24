from datetime import datetime

from pydantic import Field

from app.schemas.base import Schema, UpdateSchema


class TenantMemberCreate(Schema):
    tenant_id: int
    user_id: int
    role: str = Field(max_length=100)


class TenantMemberUpdate(UpdateSchema):
    non_nullable_fields = frozenset({"role"})

    role: str | None = Field(default=None, max_length=100)


class TenantMemberRead(TenantMemberCreate):
    id: int
    created_at: datetime
