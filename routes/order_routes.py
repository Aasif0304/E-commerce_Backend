
from fastapi import APIRouter, Depends, Form, Path, status
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User
from routes.auth_routes import get_current_user
from controllers import order_controller

router = APIRouter(
    prefix="/orders",
    tags=["Order Management"],
)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Create order from cart",
)
def create_order(
    address_id: int = Form(..., gt=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_controller.create_order(
        db,
        current_user.id,
        address_id,
    )


@router.get(
    "/",
    summary="View my orders",
)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_controller.get_my_orders(
        db,
        current_user.id,
    )


@router.get(
    "/{order_id}",
    summary="View my order details",
)
def get_order_details(
    order_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_controller.get_order_details(
        db,
        current_user.id,
        order_id,
    )
