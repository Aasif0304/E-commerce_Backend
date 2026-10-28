
from sqlalchemy.orm import Session

from services import category_service


def create_category(db: Session, name: str, description: str | None):
    return category_service.create_category(db, name, description)


def get_categories(db: Session):
    return category_service.get_categories(db)


def get_category(db: Session, category_id: int):
    return category_service.get_category(db, category_id)


def update_category(
    db: Session,
    category_id: int,
    name: str | None,
    description: str | None
):
    return category_service.update_category(
        db, category_id, name, description
    )


def delete_category(db: Session, category_id: int):
    return category_service.delete_category(db, category_id)
