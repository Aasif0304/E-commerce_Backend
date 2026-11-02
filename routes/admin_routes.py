
from fastapi import APIRouter, Depends, Path, Form
from sqlalchemy.orm import Session

from database import get_db
from models.user_model import User
from routes.auth_routes import require_admin
from controllers import admin_order_controller


router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin Order Management"],
)


@router.get(
    "/",
    summary="View all customer orders",
)
def get_all_orders(
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    return admin_order_controller.get_all_orders(db)


@router.get(
    "/{order_id}",
    summary="View any customer order details",
)
def get_order_details(
    order_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    return admin_order_controller.get_order_details(
        db,
        order_id,
    )


@router.patch(
    "/{order_id}/status",
    summary="Update customer order status",
)
def update_order_status(
    order_id: int = Path(..., ge=1),
    status: str = Form(...),
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    return admin_order_controller.update_order_status(
        db,
        order_id,
        status,
    )
