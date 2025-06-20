"""Add is_purchase column to cart_items

Revision ID: 613623054454
Revises: a47dc3df2790
Create Date: 2025-06-19 23:33:11.617058

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '613623054454'
down_revision: Union[str, None] = 'a47dc3df2790'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('cart_items', sa.Column('is_purchase', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    """Downgrade schema."""
    pass
