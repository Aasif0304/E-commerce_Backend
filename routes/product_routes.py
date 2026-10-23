
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from models.product_model import Product


router = APIRouter(prefix="/products", tags=["Products"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "img"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def save_product_image(file: UploadFile, product_id: int) -> str:
    extension = Path(file.filename or "").suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed"
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    filename = f"product_{product_id}_{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail="Image upload failed"
        )

    return f"/img/{filename}"


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_product(
    name: str = Form(...),
    price: float = Form(..., gt=0),
    stock: int = Form(..., ge=0),
    description: str | None = Form(default=None),
    image: UploadFile | None = File(default=None),
    db: Session = Depends(get_db)
):
    new_product = Product(
        name=name,
        description=description,
        price=price,
        stock=stock,
        image_url=None
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)

    if image is not None and image.filename:
        try:
            new_product.image_url = save_product_image(
                image, new_product.id
            )
            db.commit()
            db.refresh(new_product)
        except Exception:
            db.rollback()
            raise
        finally:
            image.file.close()

    return new_product


@router.post("/{product_id}/upload-image")
def upload_product_image(
    product_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        image.file.close()
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    try:
        product.image_url = save_product_image(image, product.id)
        db.commit()
        db.refresh(product)

        return {
            "message": "Product image uploaded successfully",
            "product_id": product.id,
            "image_url": product.image_url
        }
    except Exception:
        db.rollback()
        raise
    finally:
        image.file.close()


@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return db.query(Product).all()


@router.get("/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id
    ).first()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product
