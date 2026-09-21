"""modify role tables

Revision ID: 016927572017
Revises: 0ab8b0b28c57
Create Date: 2026-09-21 20:52:32.844054

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '016927572017'
down_revision: Union[str, Sequence[str], None] = '0ab8b0b28c57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
   
    op.execute("ALTER TYPE conditiontype ADD VALUE IF NOT EXISTS 'SUBTREE'")
   
def downgrade() -> None:
    """Downgrade schema."""
    pass