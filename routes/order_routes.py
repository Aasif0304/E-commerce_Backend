from fastapi import APIRouter, Depends, Form, HTTPException, Path, Request, status
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
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "address_id": {"type": "integer", "example": 1},
                        },
                        "required": ["address_id"],
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "address_id": {"type": "integer", "example": 1},
                        },
                        "required": ["address_id"],
                    }
                },
            },
        }
    },
)
async def create_order(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address_id = None
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                address_id = body.get("address_id")
        except Exception:
            pass

    if address_id is None:
        try:
            form = await request.form()
            address_id = form.get("address_id")
        except Exception:
            pass

    if address_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="address_id is required",
        )

    try:
        address_id = int(address_id)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="address_id must be a valid integer",
        )

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


@router.patch(
    "/{order_id}/cancel",
    summary="Cancel my order",
)
def cancel_order(
    order_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return order_controller.cancel_order(
        db,
        current_user.id,
        order_id,
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
