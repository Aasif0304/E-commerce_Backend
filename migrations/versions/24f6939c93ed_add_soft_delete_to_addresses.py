
"""add soft delete to addresses

Revision ID: 24f6939c93ed
Revises: fdacb4807098
Create Date: 2026-10-28 16:18:18.769773
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "24f6939c93ed"
down_revision: Union[str, Sequence[str], None] = "fdacb4807098"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "addresses",
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade() -> None:
    op.drop_column("addresses", "is_deleted")
