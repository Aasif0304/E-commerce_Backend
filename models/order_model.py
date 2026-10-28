
from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    Numeric,
    String,
    Text,
    DateTime,
    func,
)
from database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    address_id = Column(
        Integer,
        ForeignKey("addresses.id"),
        nullable=True,
    )

    recipient_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=False)
    address_line1 = Column(String(255), nullable=False)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)

    total_amount = Column(Numeric(12, 2), nullable=False)

    status = Column(
        String(30),
        nullable=False,
        default="PENDING",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
