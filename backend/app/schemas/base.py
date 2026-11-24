from typing import ClassVar

from pydantic import BaseModel, ConfigDict, model_validator


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True, extra="forbid")


class UpdateSchema(Schema):
    """Allow omitted fields, but reject null for non-nullable columns."""

    non_nullable_fields: ClassVar[frozenset[str]] = frozenset()

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        for field in self.non_nullable_fields & self.model_fields_set:
            if getattr(self, field) is None:
                raise ValueError(f"{field} cannot be null")
        return self
