from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
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
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "CONFIRMED"},
                        },
                        "required": ["status"],
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "example": "CONFIRMED"},
                        },
                        "required": ["status"],
                    }
                },
            },
        }
    },
)
async def update_order_status(
    order_id: int = Path(..., ge=1),
    request: Request = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    status_val = None
    content_type = request.headers.get("content-type", "") if request else ""
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                status_val = body.get("status")
        except Exception:
            pass

    if status_val is None and request:
        try:
            form = await request.form()
            status_val = form.get("status")
        except Exception:
            pass

    if not status_val:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="status field is required",
        )

    return admin_order_controller.update_order_status(
        db,
        order_id,
        str(status_val).strip().upper(),
    )
