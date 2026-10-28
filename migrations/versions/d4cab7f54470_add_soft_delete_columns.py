
"""add soft delete columns

Revision ID: d4cab7f54470
Revises:
Create Date: 2026-10-27 13:24:17.901124
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d4cab7f54470"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "categories",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    op.add_column(
        "products",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("products", "is_deleted")
    op.drop_column("categories", "is_deleted")
