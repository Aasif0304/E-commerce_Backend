
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from models.address_model import Address
from models.user_model import User
from routes.auth_routes import get_current_user
from schemas.address_schema import (
    AddressCreate,
    AddressUpdate,
    AddressResponse,
)

router = APIRouter(
    prefix="/addresses",
    tags=["Address Management"],
)


def get_user_address(
    address_id: int,
    user_id: int,
    db: Session,
) -> Address:
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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found",
        )

    return address


def set_default_address(
    db: Session,
    user_id: int,
    address_id: int,
) -> None:
    db.query(Address).filter(
        Address.user_id == user_id,
        Address.is_deleted.is_(False),
        Address.is_default.is_(True),
    ).update(
        {Address.is_default: False},
        synchronize_session=False,
    )

    db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id,
        Address.is_deleted.is_(False),
    ).update(
        {Address.is_default: True},
        synchronize_session=False,
    )


@router.post(
    "/",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = Address(
        user_id=current_user.id,
        recipient_name=address_data.recipient_name,
        phone=address_data.phone,
        address_line1=address_data.address_line1,
        address_line2=address_data.address_line2,
        city=address_data.city,
        state=address_data.state,
        postal_code=address_data.postal_code,
        is_default=False,
        is_deleted=False,
    )

    db.add(address)
    db.flush()

    if address_data.is_default:
        set_default_address(db, current_user.id, address.id)
    else:
        has_default = (
            db.query(Address)
            .filter(
                Address.user_id == current_user.id,
                Address.is_deleted.is_(False),
                Address.is_default.is_(True),
            )
            .first()
        )

        if not has_default:
            address.is_default = True

    db.commit()
    db.refresh(address)
    return address


@router.get("/", response_model=list[AddressResponse])
def get_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(Address)
        .filter(
            Address.user_id == current_user.id,
            Address.is_deleted.is_(False),
        )
        .order_by(Address.id.desc())
        .all()
    )


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_address(address_id, current_user.id, db)


@router.put("/{address_id}", response_model=AddressResponse)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = get_user_address(address_id, current_user.id, db)
    update_data = address_data.model_dump(exclude_unset=True)

    if update_data.get("is_default") is True:
        set_default_address(db, current_user.id, address.id)

    for field, value in update_data.items():
        setattr(address, field, value)

    db.commit()
    db.refresh(address)
    return address


@router.delete("/{address_id}")
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = get_user_address(address_id, current_user.id, db)

    active_addresses = (
        db.query(Address)
        .filter(
            Address.user_id == current_user.id,
            Address.is_deleted.is_(False),
        )
        .count()
    )

    if active_addresses == 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your only active address",
        )

    was_default = address.is_default

    address.is_deleted = True
    address.is_default = False
    db.flush()

    if was_default:
        next_address = (
            db.query(Address)
            .filter(
                Address.user_id == current_user.id,
                Address.is_deleted.is_(False),
            )
            .order_by(Address.id.desc())
            .first()
        )

        if next_address:
            next_address.is_default = True

    db.commit()

    return {"message": "Address deleted successfully"}
