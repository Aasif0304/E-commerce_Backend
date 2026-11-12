
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session, joinedload, selectinload

from models.product_model import Product
from models.product_image_model import ProductImage
from models.category_model import Category


UPLOAD_DIR = Path(__file__).resolve().parent.parent / "img"
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def filter_valid_images(images: list[UploadFile] | None) -> list[UploadFile]:
    """Return uploaded image files that have a non-empty filename."""
    if not images:
        return []
    return [img for img in images if img and img.filename and img.filename.strip()]


def close_upload_files(images: list[UploadFile] | None) -> None:
    """Close any open UploadFile streams."""
    if not images:
        return
    for image in images:
        if image and image.file and not image.file.closed:
            image.file.close()


def validate_image_extensions(images: list[UploadFile]) -> None:
    """Validate that all uploaded files have allowed image extensions."""
    for image in images:
        extension = Path(image.filename or "").suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail="Only JPG, JPEG, PNG and WEBP images are allowed",
            )


def save_image(image: UploadFile, product_id: int) -> str:
    extension = Path(image.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, JPEG, PNG and WEBP images are allowed",
        )

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"product_{product_id}_{uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    except Exception:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail="Image upload failed",
        )

    return f"/img/{filename}"


def save_images(images: list[UploadFile], product_id: int) -> list[str]:
    """Validate and save multiple images for a product, rolling back saved files on error."""
    validate_image_extensions(images)
    saved_urls: list[str] = []
    try:
        for image in images:
            saved_urls.append(save_image(image, product_id))
        return saved_urls
    except Exception:
        remove_images(saved_urls, ignore_os_error=True)
        raise


def remove_image(image_url: str | None) -> None:
    if not image_url or not image_url.startswith("/img/"):
        return

    filename = image_url.removeprefix("/img/")
    if Path(filename).name == filename:
        (UPLOAD_DIR / filename).unlink(missing_ok=True)


def remove_images(image_urls: list[str], ignore_os_error: bool = False) -> None:
    """Delete local image files for the given image URLs."""
    for image_url in image_urls:
        try:
            remove_image(image_url)
        except OSError:
            if not ignore_os_error:
                raise


def validate_category(db: Session, category_id: int | None):
    if category_id is None:
        return

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


def create_product(
    db: Session,
    name: str,
    price: float,
    stock: int,
    description: str | None,
    images: list[UploadFile] | None,
    category_id: int | None = None,
):
    valid_images = filter_valid_images(images)
    saved_urls: list[str] = []
    try:
        validate_category(db, category_id)
        validate_image_extensions(valid_images)

        product = Product(
            name=name,
            price=price,
            stock=stock,
            description=description,
            image_url=None,
            category_id=category_id,
            is_deleted=False,
        )
        db.add(product)
        db.flush()

        if valid_images:
            saved_urls = save_images(valid_images, product.id)
            product.image_url = saved_urls[0]
            for url in saved_urls:
                db.add(ProductImage(product_id=product.id, image_url=url))

        db.commit()
        return get_product(db, product.id)
    except Exception:
        db.rollback()
        if saved_urls:
            remove_images(saved_urls, ignore_os_error=True)
        raise
    finally:
        close_upload_files(images)


def get_products(db: Session):
    return (
        db.query(Product)
        .options(joinedload(Product.category), selectinload(Product.images))
        .filter(Product.is_deleted.is_(False))
        .order_by(Product.id)
        .all()
    )


def get_product(db: Session, product_id: int):
    product = (
        db.query(Product)
        .options(joinedload(Product.category), selectinload(Product.images))
        .filter(
            Product.id == product_id,
            Product.is_deleted.is_(False),
        )
        .first()
    )
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )
    return product


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
    valid_images = filter_valid_images(images)
    try:
        product = get_product(db, product_id)

        if (
            name is None
            and price is None
            and stock is None
            and description is None
            and category_id is None
            and not valid_images
        ):
            raise HTTPException(
                status_code=400,
                detail="No fields to update",
            )

        validate_category(db, category_id)
        validate_image_extensions(valid_images)
    except Exception:
        close_upload_files(images)
        raise

    old_images = [img.image_url for img in product.images]
    if product.image_url and product.image_url not in old_images:
        old_images.append(product.image_url)

    new_images: list[str] = []
    try:
        if name is not None:
            product.name = name
        if price is not None:
            product.price = price
        if stock is not None:
            product.stock = stock
        if description is not None:
            product.description = description
        if category_id is not None:
            product.category_id = category_id
        if valid_images:
            new_images = save_images(valid_images, product.id)
            product.images.clear()
            for url in new_images:
                product.images.append(ProductImage(image_url=url))
            product.image_url = new_images[0]

        db.commit()
    except Exception:
        db.rollback()
        if new_images:
            remove_images(new_images, ignore_os_error=True)
        raise
    finally:
        close_upload_files(images)

    if new_images and old_images:
        remove_images(old_images, ignore_os_error=True)

    return get_product(db, product_id)


def delete_product(db: Session, product_id: int):
    product = get_product(db, product_id)
    product.is_deleted = True
    db.commit()
    return {
        "message": "Product deleted successfully",
        "product_id": product_id,
    }
