
from pydantic import AliasPath, BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=150,
        description="Name of the product",
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Detailed description of the product",
    )
    price: float = Field(
        gt=0,
        description="Product price in INR",
    )
    stock: int = Field(
        ge=0,
        description="Stock quantity available",
    )
    category_id: int | None = Field(
        default=None,
        gt=0,
        description="ID of the product category",
    )
    image_url: str | None = Field(
        default=None,
        description="URL or path of the product image",
    )


class ProductResponse(BaseModel):
    id: int = Field(
        ...,
        description="Unique product identifier",
        examples=[1],
    )
    name: str = Field(
        ...,
        description="Name of the product",
        examples=["Laptop"],
    )
    description: str | None = Field(
        default=None,
        description="Detailed description of the product",
        examples=["Dell Inspiron 15 Laptop with 16GB RAM"],
    )
    price: float = Field(
        ...,
        description="Product price in INR",
        examples=[55000.00],
    )
    stock: int = Field(
        ...,
        description="Available stock quantity",
        examples=[10],
    )
    image_url: str | None = Field(
        default=None,
        description="Image URL of the product",
        examples=["/img/product_1_example.jpg"],
    )
    category_id: int | None = Field(
        default=None,
        description="ID of the product category",
    )
    category_name: str | None = Field(
        default=None,
        description="Name of the product category",
        validation_alias=AliasPath("category", "name"),
    )

    model_config = ConfigDict(from_attributes=True)


class ProductDeleteResponse(BaseModel):
    message: str = Field(
        ...,
        description="Status message of the deletion",
        examples=["Product deleted successfully"],
    )
    product_id: int = Field(
        ...,
        description="ID of the deleted product",
        examples=[1],
    )
