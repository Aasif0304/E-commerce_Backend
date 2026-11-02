
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.order_model import Order
from models.order_item_model import OrderItem
from models.product_model import Product


ALLOWED_STATUS_TRANSITIONS = {
    "PENDING": ["CONFIRMED", "CANCELLED"],
    "CONFIRMED": ["SHIPPED", "CANCELLED"],
    "SHIPPED": ["DELIVERED"],
    "DELIVERED": [],
    "CANCELLED": [],
}


def get_all_orders(db: Session):
    orders = (
        db.query(Order)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .all()
    )

    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "recipient_name": order.recipient_name,
            "phone": order.phone,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "created_at": order.created_at,
        }
        for order in orders
    ]


def get_order_details(db: Session, order_id: int):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    order_items = (
        db.query(OrderItem)
        .filter(OrderItem.order_id == order.id)
        .order_by(OrderItem.id.asc())
        .all()
    )

    return {
        "id": order.id,
        "user_id": order.user_id,
        "address_id": order.address_id,
        "delivery_address": {
            "recipient_name": order.recipient_name,
            "phone": order.phone,
            "address_line1": order.address_line1,
            "address_line2": order.address_line2,
            "city": order.city,
            "state": order.state,
            "postal_code": order.postal_code,
        },
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product_name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "subtotal": float(item.subtotal),
            }
            for item in order_items
        ],
        "total_amount": float(order.total_amount),
        "status": order.status,
        "created_at": order.created_at,
    }


def update_order_status(
    db: Session,
    order_id: int,
    new_status: str,
):
    new_status = new_status.strip().upper()

    if new_status not in ALLOWED_STATUS_TRANSITIONS:
        raise HTTPException(
            status_code=400,
            detail="Invalid order status",
        )

    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .with_for_update()
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    allowed_statuses = ALLOWED_STATUS_TRANSITIONS[order.status]

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change order status from {order.status} to {new_status}",
        )

    try:
        if new_status == "CANCELLED":
            order_items = (
                db.query(OrderItem)
                .filter(OrderItem.order_id == order.id)
                .all()
            )

            for item in order_items:
                product = (
                    db.query(Product)
                    .filter(Product.id == item.product_id)
                    .with_for_update()
                    .first()
                )

                if product:
                    product.stock += item.quantity

        order.status = new_status

        db.commit()
        db.refresh(order)

        return get_order_details(db, order.id)

    except Exception:
        db.rollback()
        raise
