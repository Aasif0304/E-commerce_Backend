"""add product_images table for multiple product images

Revision ID: 8f3a1c2d9e4b
Revises: 24f6939c93ed
Create Date: 2026-11-12 11:42:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8f3a1c2d9e4b"
down_revision: Union[str, Sequence[str], None] = "24f6939c93ed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "product_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_product_images_id"),
        "product_images",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_product_images_product_id"),
        "product_images",
        ["product_id"],
        unique=False,
    )

    op.execute(
        """
        INSERT INTO product_images (product_id, image_url)
        SELECT id, image_url
        FROM products
        WHERE image_url IS NOT NULL AND image_url <> ''
        """
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_product_images_product_id"),
        table_name="product_images",
    )
    op.drop_index(
        op.f("ix_product_images_id"),
        table_name="product_images",
    )
    op.drop_table("product_images")

