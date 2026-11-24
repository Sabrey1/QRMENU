from pydantic import Field, SecretStr, field_validator

from app.schemas.base import Schema
from app.schemas.tenants import TenantRead
from app.schemas.users import UserRead


class LoginRequest(Schema):
    email: str
    password: SecretStr


class RegisterRequest(Schema):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=3, max_length=255)
    password: SecretStr = Field(min_length=8, max_length=128)
    currency_code: str = Field(default="KHR", pattern=r"^[A-Z]{3}$")

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be empty")
        return value


class RegisterResponse(UserRead):
    tenant: TenantRead


class Token(Schema):
    access_token: str
    token_type: str = "bearer"
