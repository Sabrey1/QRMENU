from datetime import datetime

from pydantic import Field, SecretStr

from app.schemas.base import Schema, UpdateSchema


class UserCreate(Schema):
    name: str = Field(max_length=100)
    email: str = Field(max_length=255)
    password: SecretStr
    is_active: bool = True


class UserUpdate(UpdateSchema):
    non_nullable_fields = frozenset({"name", "email", "password", "is_active"})

    name: str | None = Field(default=None, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    password: SecretStr | None = None
    is_active: bool | None = None


class UserRead(Schema):
    id: int
    name: str
    email: str
    is_active: bool
    created_at: datetime
