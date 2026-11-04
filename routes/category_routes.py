from fastapi import APIRouter, Depends, HTTPException, Path, Request, status
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
    openapi_extra={
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "example": "Electronics"},
                            "description": {"type": "string", "example": "Devices and gadgets"},
                        },
                        "required": ["name"],
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "example": "Electronics"},
                            "description": {"type": "string", "example": "Devices and gadgets"},
                        },
                        "required": ["name"],
                    }
                },
            },
        }
    },
)
async def create_category(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    name = None
    description = None

    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                name = body.get("name")
                description = body.get("description")
        except Exception:
            pass

    if name is None:
        try:
            form = await request.form()
            name = form.get("name")
            description = form.get("description")
        except Exception:
            pass

    if not name or not str(name).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name cannot be empty",
        )

    return category_controller.create_category(
        db,
        str(name).strip(),
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
    openapi_extra={
        "requestBody": {
            "required": False,
            "content": {
                "application/json": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "example": "Updated Category"},
                            "description": {"type": "string", "example": "Updated description"},
                        },
                    }
                },
                "application/x-www-form-urlencoded": {
                    "schema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string", "example": "Updated Category"},
                            "description": {"type": "string", "example": "Updated description"},
                        },
                    }
                },
            },
        }
    },
)
async def update_category(
    category_id: int = Path(..., ge=1),
    request: Request = None,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    name = None
    description = None

    content_type = request.headers.get("content-type", "") if request else ""
    if "application/json" in content_type:
        try:
            body = await request.json()
            if isinstance(body, dict):
                name = body.get("name")
                description = body.get("description")
        except Exception:
            pass

    if name is None and description is None and request:
        try:
            form = await request.form()
            name = form.get("name")
            description = form.get("description")
        except Exception:
            pass

    if name is not None and not str(name).strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name cannot be empty",
        )

    return category_controller.update_category(
        db,
        category_id,
        str(name).strip() if name is not None else None,
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
