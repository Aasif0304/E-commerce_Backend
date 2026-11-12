
from fastapi import UploadFile
from sqlalchemy.orm import Session

from services import product_service


def create_product(
    db: Session,
    name: str,
    price: float,
    stock: int,
    description: str | None,
    images: list[UploadFile] | None,
    category_id: int | None = None,
):
    return product_service.create_product(
        db,
        name,
        price,
        stock,
        description,
        images,
        category_id,
    )


def get_products(db: Session):
    return product_service.get_products(db)


def get_product(db: Session, product_id: int):
    return product_service.get_product(db, product_id)


def update_product(
    db: Session,
    product_id: int,
    name: str | None,
    price: float | None,
    stock: int | None,
    description: str | None,
    images: list[UploadFile] | None,
    category_id: int | None = None,
):
    return product_service.update_product(
        db,
        product_id,
        name,
        price,
        stock,
        description,
        images,
        category_id,
    )


def delete_product(db: Session, product_id: int):
    return product_service.delete_product(db, product_id)
