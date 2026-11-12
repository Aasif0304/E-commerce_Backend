
from sqlalchemy import (Column,Integer,String,Text,Numeric,Boolean,ForeignKey,)
from sqlalchemy.orm import relationship

from database import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    image_url = Column(String(500), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=True,
        index=True,
    )

    category = relationship("Category")
    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductImage.id",
    )

    @property
    def image_urls(self) -> list[str]:
        if self.images:
            return [img.image_url for img in self.images]
        if self.image_url:
            return [self.image_url]
        return []
