from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.cart_model import CartItem
from models.product_model import Product


def add_to_cart(
    db: Session,
    user_id: int,
    product_id: int,
    quantity: int,
):
    product = (
        db.query(Product)
        .filter(
            Product.id == product_id,
            Product.is_deleted == False,
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user_id,
            CartItem.product_id == product_id,
        )
        .first()
    )

    existing_quantity = cart_item.quantity if cart_item else 0
    new_quantity = existing_quantity + quantity

    if new_quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available stock: {product.stock}",
        )

    if cart_item:
        cart_item.quantity = new_quantity
    else:
        cart_item = CartItem(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Product added to cart successfully",
        "cart_item_id": cart_item.id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity,
    }


def get_my_cart(db: Session, user_id: int):
    cart_items = (
        db.query(CartItem, Product)
        .join(Product, CartItem.product_id == Product.id)
        .filter(
            CartItem.user_id == user_id,
            Product.is_deleted == False,
        )
        .all()
    )

    items = []
    total_amount = 0

    for cart_item, product in cart_items:
        subtotal = product.price * cart_item.quantity
        total_amount += subtotal

        items.append({
            "cart_item_id": cart_item.id,
            "product_id": product.id,
            "product_name": product.name,
            "price": float(product.price),
            "quantity": cart_item.quantity,
            "stock": product.stock,
            "subtotal": float(subtotal),
            "image_url": product.image_url,
        })

    return {
        "items": items,
        "total_items": len(items),
        "total_amount": float(total_amount),
    }


def update_cart_quantity(
    db: Session,
    user_id: int,
    cart_item_id: int,
    quantity: int,
):
    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail="Quantity must be greater than zero",
        )

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id,
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    product = (
        db.query(Product)
        .filter(
            Product.id == cart_item.product_id,
            Product.is_deleted == False,
        )
        .first()
    )

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    if quantity > product.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient stock. Available stock: {product.stock}",
        )

    cart_item.quantity = quantity

    db.commit()
    db.refresh(cart_item)

    return {
        "message": "Cart quantity updated successfully",
        "cart_item_id": cart_item.id,
        "product_id": cart_item.product_id,
        "quantity": cart_item.quantity,
    }


def remove_from_cart(
    db: Session,
    user_id: int,
    cart_item_id: int,
):
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.user_id == user_id,
        )
        .first()
    )

    if not cart_item:
        raise HTTPException(
            status_code=404,
            detail="Cart item not found",
        )

    db.delete(cart_item)
    db.commit()

    return {
        "message": "Product removed from cart successfully",
        "cart_item_id": cart_item_id,
    }


def clear_my_cart(db: Session, user_id: int):
    deleted_count = (
        db.query(CartItem)
        .filter(CartItem.user_id == user_id)
        .delete(synchronize_session=False)
    )

    db.commit()

    return {
        "message": "Cart cleared successfully",
        "removed_items": deleted_count,
    }