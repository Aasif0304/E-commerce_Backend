
from pydantic import BaseModel, ConfigDict, Field


class AddressCreate(BaseModel):
    recipient_name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=10, max_length=20)
    address_line1: str = Field(min_length=1, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=1, max_length=20)
    is_default: bool = False


class AddressUpdate(BaseModel):
    recipient_name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, min_length=10, max_length=20)
    address_line1: str | None = Field(default=None, min_length=1, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=1, max_length=100)
    postal_code: str | None = Field(default=None, min_length=1, max_length=20)
    is_default: bool | None = None


class AddressResponse(BaseModel):
    id: int
    user_id: int
    recipient_name: str
    phone: str
    address_line1: str
    address_line2: str | None
    city: str
    state: str
    postal_code: str
    is_default: bool

    model_config = ConfigDict(from_attributes=True)
