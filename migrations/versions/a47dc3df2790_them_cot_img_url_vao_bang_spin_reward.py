"""them cot img_url vao bang spin_reward

Revision ID: a47dc3df2790
Revises: 
Create Date: 2025-05-07 10:53:47.771137

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a47dc3df2790'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("spin_rewards", sa.Column("reward_img_url", sa.String(50)))


def downgrade() -> None:
    """Downgrade schema."""
    pass
