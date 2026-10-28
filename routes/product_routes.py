
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from database import get_db
from controllers import product_controller
from routes.auth_routes import require_admin
from schemas.product_schema import ProductDeleteResponse, ProductResponse

router = APIRouter(prefix="/products", tags=["Products"])


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a product",
    description="Add a new product with details and optional image upload.",
)
def create_product(
    name: str = Form(default="", description="Product name"),
    price: float | None = Form(default=None, description="Price in INR"),
    stock: int | None = Form(default=None, description="Stock quantity"),
    description: str | None = Form(
        default=None,
        description="Product description",
    ),
    image: UploadFile | None = File(
        default=None,
        description="Optional image file",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if not name or not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product name is required",
        )

    if price is None or price <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product price must be greater than 0",
        )

    if stock is None or stock < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Stock must be 0 or greater",
        )

    return product_controller.create_product(
        db, name.strip(), price, stock, description, image
    )


@router.get(
    "/",
    response_model=list[ProductResponse],
    summary="Get all products",
    description="Retrieve the complete list of products from the database.",
)
def get_products(db: Session = Depends(get_db)):
    return product_controller.get_products(db)


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Get product by ID",
    description="Retrieve a single product by its unique product ID.",
)
def get_product(
    product_id: int = Path(
        ...,
        ge=1,
        description="Unique product ID",
    ),
    db: Session = Depends(get_db),
):
    return product_controller.get_product(db, product_id)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    summary="Update a product",
    description=(
        "Update product details and/or replace the product image. "
        "Omitted fields remain unchanged."
    ),
)
def update_product(
    product_id: int = Path(
        ...,
        ge=1,
        description="Unique ID of the product to update",
    ),
    name: str | None = Form(
        default=None,
        description="Product name",
    ),
    price: float | None = Form(
        default=None,
        description="Price in INR",
    ),
    stock: int | None = Form(
        default=None,
        description="Stock quantity",
    ),
    description: str | None = Form(
        default=None,
        description="Product description",
    ),
    image: UploadFile | None = File(
        default=None,
        description="New image file",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        product_controller.get_product(db, product_id)

        if name is not None and not name.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product name cannot be empty",
            )

        if price is not None and price <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product price must be greater than 0",
            )

        if stock is not None and stock < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock must be 0 or greater",
            )

        if name is not None:
            name = name.strip()

        return product_controller.update_product(
            db, product_id, name, price, stock, description, image
        )

    finally:
        if image and not image.file.closed:
            image.file.close()


@router.delete(
    "/{product_id}",
    response_model=ProductDeleteResponse,
    summary="Delete a product",
    description="Soft-delete a product so it no longer appears in product listings.",
)
def delete_product(
    product_id: int = Path(
        ...,
        ge=1,
        description="Unique product ID",
    ),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return product_controller.delete_product(db, product_id)
