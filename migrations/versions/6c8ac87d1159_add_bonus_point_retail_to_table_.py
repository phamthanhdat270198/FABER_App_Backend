"""Add bonus point retail to table typedetails

Revision ID: 6c8ac87d1159
Revises: b99829d59fa4
Create Date: 2025-09-18 23:51:38.665095

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c8ac87d1159'
down_revision: Union[str, None] = 'b99829d59fa4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("type_details", sa.Column("bonus_points_retail", sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    pass
