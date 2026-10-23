
from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
        examples=["Laptop"]
    )
    description: str | None = Field(
        default=None,
        examples=["Dell Inspiron Laptop"]
    )
    price: float = Field(
        gt=0,
        examples=[55000.00]
    )
    stock: int = Field(
        ge=0,
        examples=[10]
    )
    image_url: str | None = Field(
        default=None,
        examples=["https://example.com/laptop.jpg"]
    )


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: float
    stock: int
    image_url: str | None

    model_config = ConfigDict(from_attributes=True)
