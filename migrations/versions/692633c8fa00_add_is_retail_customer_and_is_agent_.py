"""Add is_retail_customer and is_agent columns

Revision ID: 692633c8fa00
Revises: 613623054454
Create Date: 2025-06-24 23:26:38.332848

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '692633c8fa00'
down_revision: Union[str, None] = '613623054454'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('is_retail_customer', sa.Boolean(), nullable=False, server_default='true'))
    op.add_column('users', sa.Column('is_agent', sa.Boolean(), nullable=False, server_default='false'))



def downgrade() -> None:
    """Downgrade schema."""
    pass
