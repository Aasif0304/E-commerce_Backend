
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from models.product_model import Product


UPLOAD_DIR = Path(__file__).resolve().parent.parent / "img"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def save_image(image: UploadFile, product_id: int) -> str:
    extension = Path(image.filename or "").suffix.lower()

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
            shutil.copyfileobj(image.file, buffer)
    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Image upload failed")

    return f"/img/{filename}"


def remove_image(image_url: str | None) -> None:
    if not image_url or not image_url.startswith("/img/"):
        return

    filename = image_url.removeprefix("/img/")

    if Path(filename).name == filename:
        (UPLOAD_DIR / filename).unlink(missing_ok=True)


def create_product(db: Session, name: str, price: float, stock: int,
                   description: str | None, image: UploadFile | None):
    image_url = None

    try:
        product = Product(
            name=name,
            price=price,
            stock=stock,
            description=description,
            image_url=None
        )

        db.add(product)
        db.flush()

        if image and image.filename:
            image_url = save_image(image, product.id)
            product.image_url = image_url

        db.commit()
        db.refresh(product)
        return product

    except Exception:
        db.rollback()
        if image_url:
            remove_image(image_url)
        raise

    finally:
        if image:
            image.file.close()


def get_products(db: Session):
    return db.query(Product).all()


def get_product(db: Session, product_id: int):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


def update_product(db: Session, product_id: int, name: str | None,
                   price: float | None, stock: int | None,
                   description: str | None, image: UploadFile | None):
    product = get_product(db, product_id)

    if (
        name is None and price is None and stock is None
        and description is None and not (image and image.filename)
    ):
        if image:
            image.file.close()
        raise HTTPException(status_code=400, detail="No fields to update")

    old_image = product.image_url
    new_image = None

    try:
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = stock
        if description is not None:
            product.description = description

        if image and image.filename:
            new_image = save_image(image, product.id)
            product.image_url = new_image

        db.commit()
        db.refresh(product)

    except Exception:
        db.rollback()
        if new_image:
            remove_image(new_image)
        raise

    finally:
        if image:
            image.file.close()

    if new_image and old_image:
        try:
            remove_image(old_image)
        except OSError:
            pass

    return product


def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    old_image = product.image_url

    try:
        db.delete(product)
        db.commit()
    except Exception:
        db.rollback()
        raise

    if old_image:
        try:
            remove_image(old_image)
        except OSError:
            pass

    return {"message": "Product deleted successfully", "product_id": product_id}
