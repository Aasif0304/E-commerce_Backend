from fastapi import APIRouter, Depends, Form, HTTPException, Path, status
from sqlalchemy.orm import Session

from database import get_db
from controllers import category_controller
from schemas.category_schema import (
    CategoryResponse,
    CategoryDeleteResponse,
)
from routes.auth_routes import require_admin

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
)
def create_category(
    name: str = Form(..., min_length=1, max_length=100),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if not name.strip():
        raise HTTPException(
            status_code=400,
            detail="Category name cannot be empty",
        )

    return category_controller.create_category(
        db,
        name.strip(),
        description,
    )


@router.get(
    "/",
    response_model=list[CategoryResponse],
    summary="Get all categories",
)
def get_categories(db: Session = Depends(get_db)):
    return category_controller.get_categories(db)


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Get category by ID",
)
def get_category(
    category_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
):
    return category_controller.get_category(db, category_id)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Update a category",
)
def update_category(
    category_id: int = Path(..., ge=1),
    name: str | None = Form(default=None, min_length=1, max_length=100),
    description: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    if name is not None and not name.strip():
        raise HTTPException(
            status_code=400,
            detail="Category name cannot be empty",
        )

    return category_controller.update_category(
        db,
        category_id,
        name.strip() if name is not None else None,
        description,
    )


@router.delete(
    "/{category_id}",
    response_model=CategoryDeleteResponse,
    summary="Delete a category",
)
def delete_category(
    category_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    return category_controller.delete_category(db, category_id)