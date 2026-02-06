"""Company Pydantic schemas with camelCase serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase."""
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class CompanyBase(BaseModel):
    """Base schema for Company - shared fields."""

    name: str
    url: Optional[str] = None


class CompanyCreate(CompanyBase):
    """Schema for creating a new Company."""

    pass


class CompanyUpdate(BaseModel):
    """Schema for updating a Company - all fields optional."""

    name: Optional[str] = None
    url: Optional[str] = None


class CompanyRead(CompanyBase):
    """Schema for reading a Company - includes all fields."""

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,  # Enable ORM mode
        alias_generator=to_camel,  # Convert to camelCase
        populate_by_name=True,  # Allow both snake_case and camelCase input
    )


class CompanyList(BaseModel):
    """Schema for list of companies."""

    items: list[CompanyRead]
    total: int
