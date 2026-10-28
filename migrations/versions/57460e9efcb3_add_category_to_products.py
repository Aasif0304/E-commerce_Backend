"""add category to products

Revision ID: 57460e9efcb3
Revises: c8786844d894
Create Date: 2026-10-28 11:20:28.521922

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57460e9efcb3'
down_revision: Union[str, Sequence[str], None] = 'c8786844d894'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "products",
        sa.Column("category_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        op.f("ix_products_category_id"),
        "products",
        ["category_id"],
        unique=False,
    )
    op.create_foreign_key(
        "fk_products_category_id_categories",
        "products",
        "categories",
        ["category_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_products_category_id_categories",
        "products",
        type_="foreignkey",
    )
    op.drop_index(
        op.f("ix_products_category_id"),
        table_name="products",
    )
    op.drop_column("products", "category_id")