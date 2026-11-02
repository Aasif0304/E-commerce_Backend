
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.address_model import Address
from models.cart_model import CartItem
from models.order_item_model import OrderItem
from models.order_model import Order
from models.product_model import Product


def create_order(db: Session, user_id: int, address_id: int):
    try:
        address = (
            db.query(Address)
            .filter(
                Address.id == address_id,
                Address.user_id == user_id,
                Address.is_deleted.is_(False),
            )
            .first()
        )

        if not address:
            raise HTTPException(
                status_code=404,
                detail="Active delivery address not found",
            )

        cart_items = (
            db.query(CartItem)
            .filter(CartItem.user_id == user_id)
            .with_for_update()
            .all()
        )

        if not cart_items:
            raise HTTPException(
                status_code=400,
                detail="Your cart is empty",
            )

        order_lines = []
        total_amount = Decimal("0.00")

        for cart_item in cart_items:
            product = (
                db.query(Product)
                .filter(
                    Product.id == cart_item.product_id,
                    Product.is_deleted.is_(False),
                )
                .with_for_update()
                .first()
            )

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product ID {cart_item.product_id} not found or inactive",
                )

            if cart_item.quantity <= 0:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid quantity for product ID {product.id}",
                )

            if product.stock < cart_item.quantity:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Insufficient stock for '{product.name}'. "
                        f"Available stock: {product.stock}"
                    ),
                )

            unit_price = Decimal(str(product.price))
            subtotal = unit_price * cart_item.quantity
            total_amount += subtotal

            order_lines.append(
                {
                    "cart_item": cart_item,
                    "product": product,
                    "product_name": product.name,
                    "quantity": cart_item.quantity,
                    "unit_price": unit_price,
                    "subtotal": subtotal,
                }
            )

        order = Order(
            user_id=user_id,
            address_id=address.id,
            recipient_name=address.recipient_name,
            phone=address.phone,
            address_line1=address.address_line1,
            address_line2=address.address_line2,
            city=address.city,
            state=address.state,
            postal_code=address.postal_code,
            total_amount=total_amount,
            status="PENDING",
        )

        db.add(order)
        db.flush()

        for line in order_lines:
            order_item = OrderItem(
                order_id=order.id,
                product_id=line["product"].id,
                product_name=line["product_name"],
                quantity=line["quantity"],
                unit_price=line["unit_price"],
                subtotal=line["subtotal"],
            )

            db.add(order_item)
            line["product"].stock -= line["quantity"]

        for line in order_lines:
            db.delete(line["cart_item"])

        db.commit()
        db.refresh(order)

        return get_order_details(db, user_id, order.id)

    except Exception:
        db.rollback()
        raise


def get_my_orders(db: Session, user_id: int):
    orders = (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .all()
    )

    return [
        {
            "id": order.id,
            "user_id": order.user_id,
            "address_id": order.address_id,
            "recipient_name": order.recipient_name,
            "phone": order.phone,
            "address_line1": order.address_line1,
            "address_line2": order.address_line2,
            "city": order.city,
            "state": order.state,
            "postal_code": order.postal_code,
            "total_amount": float(order.total_amount),
            "status": order.status,
            "created_at": order.created_at,
        }
        for order in orders
    ]


def get_order_details(db: Session, user_id: int, order_id: int):
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found",
        )

    return _build_order_details(db, order)


def _build_order_details(db: Session, order: Order):
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


def cancel_order(db: Session, user_id: int, order_id: int):
    try:
        order = (
            db.query(Order)
            .filter(
                Order.id == order_id,
                Order.user_id == user_id,
            )
            .with_for_update()
            .first()
        )

        if not order:
            raise HTTPException(
                status_code=404,
                detail="Order not found",
            )

        if order.status not in ["PENDING", "CONFIRMED"]:
            raise HTTPException(
                status_code=400,
                detail=f"Order cannot be cancelled because its status is {order.status}",
            )

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

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product ID {item.product_id} not found",
                )

            product.stock += item.quantity

        order.status = "CANCELLED"

        db.commit()
        db.refresh(order)

        return _build_order_details(db, order)

    except Exception:
        db.rollback()
        raise
