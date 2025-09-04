"""Add column customer retail price to type detail

Revision ID: 0bec742a37ac
Revises: 692633c8fa00
Create Date: 2025-09-04 23:52:00.656365

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bec742a37ac'
down_revision: Union[str, None] = '692633c8fa00'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("type_details", sa.Column("retail_price", sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
