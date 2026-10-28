from fastapi import APIRouter, Depends, Form, Path, status
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
)
def add_to_cart(
    product_id: int = Form(..., gt=0),
    quantity: int = Form(1, gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
)
def update_cart_quantity(
    cart_item_id: int = Path(..., ge=1),
    quantity: int = Form(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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