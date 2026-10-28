
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.category_model import Category


def create_category(db: Session, name: str, description: str | None):
    category = Category(
        name=name.strip(),
        description=description,
        is_deleted=False,
    )

    db.add(category)

    try:
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A category with this name already exists",
        )


def get_categories(db: Session):
    return (
        db.query(Category)
        .filter(Category.is_deleted.is_(False))
        .order_by(Category.id)
        .all()
    )


def get_category(db: Session, category_id: int):
    category = (
        db.query(Category)
        .filter(
            Category.id == category_id,
            Category.is_deleted.is_(False),
        )
        .first()
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return category


def update_category(
    db: Session,
    category_id: int,
    name: str | None,
    description: str | None,
):
    category = get_category(db, category_id)

    if name is None and description is None:
        raise HTTPException(
            status_code=400,
            detail="Provide at least one field to update",
        )

    if name is not None:
        category.name = name.strip()

    if description is not None:
        category.description = description

    try:
        db.commit()
        db.refresh(category)
        return category
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A category with this name already exists",
        )


def delete_category(db: Session, category_id: int):
    category = get_category(db, category_id)

    category.is_deleted = True

    db.commit()

    return {
        "message": "Category deleted successfully",
        "category_id": category_id,
    }
