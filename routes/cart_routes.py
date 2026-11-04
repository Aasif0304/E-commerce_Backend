from fastapi import APIRouter, Depends, Form, HTTPException, Path, Request, status
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User
from routes.auth_routes import get_current_user
from controllers import cart_controller

router = APIRouter(prefix="/cart", tags=["Cart Management"])


@router.post(
    "/items",
    status_code=status.HTTP_201_CREATED,
    summary="Add product to cart",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "integer", "example": 1},
                            "quantity": {"type": "integer", "example": 1, "default": 1},
                        },
                        "required": ["product_id"],
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "product_id": {"type": "integer", "example": 1},
                            "quantity": {"type": "integer", "example": 1, "default": 1},
                        },
                        "required": ["product_id"],
                    }
                },
            },
        }
    },
)
async def add_to_cart(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    product_id = None
    quantity = 1

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                product_id = body.get("product_id")
                quantity = body.get("quantity", 1)
        except Exception:
            pass

    if product_id is None:
        try:
            form = await request.form()
            product_id = form.get("product_id")
            quantity = form.get("quantity", 1)
        except Exception:
            pass

    if product_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="product_id is required",
        )

    try:
        product_id = int(product_id)
        quantity = int(quantity)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="product_id and quantity must be valid integers",
        )

    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero",
        )

    return cart_controller.add_to_cart(
        db,
        current_user.id,
        product_id,
        quantity,
    )


@router.get(
    "/",
    summary="View my cart",
)
def get_my_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cart_controller.get_my_cart(
        db,
        current_user.id,
    )


@router.put(
    "/items/{cart_item_id}",
    summary="Update cart item quantity",
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "quantity": {"type": "integer", "example": 2},
                        },
                        "required": ["quantity"],
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "quantity": {"type": "integer", "example": 2},
                        },
                        "required": ["quantity"],
                    }
                },
            },
        }
    },
)
async def update_cart_quantity(
    cart_item_id: int = Path(..., ge=1),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quantity = None
    content_type = request.headers.get("content-type", "") if request else ""
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                quantity = body.get("quantity")
        except Exception:
            pass

    if quantity is None and request:
        try:
            form = await request.form()
            quantity = form.get("quantity")
        except Exception:
            pass

    if quantity is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="quantity is required",
        )

    try:
        quantity = int(quantity)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="quantity must be a valid integer",
        )

    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantity must be greater than zero",
        )

    return cart_controller.update_cart_quantity(
        db,
        current_user.id,
        cart_item_id,
        quantity,
    )


@router.delete(
    "/items/{cart_item_id}",
    summary="Remove item from cart",
)
def remove_from_cart(
    cart_item_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cart_controller.remove_from_cart(
        db,
        current_user.id,
        cart_item_id,
    )


@router.delete(
    "/",
    summary="Clear my cart",
)
def clear_my_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cart_controller.clear_my_cart(
        db,
        current_user.id,
    )
