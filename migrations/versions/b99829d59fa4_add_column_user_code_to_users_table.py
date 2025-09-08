"""Add column user_code to users table

Revision ID: b99829d59fa4
Revises: 0bec742a37ac
Create Date: 2025-09-08 11:01:39.496847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b99829d59fa4'
down_revision: Union[str, None] = '0bec742a37ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("user_code", sa.String(50)))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "user_code")
