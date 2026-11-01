"""Add new ConditionType - ORGANIZATION

Revision ID: e842ed0b5837
Revises: 5c25362a2779
Create Date: 2026-11-01 16:12:39.177075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e842ed0b5837'
down_revision: Union[str, Sequence[str], None] = '5c25362a2779'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade() -> None:
    op.execute("ALTER TYPE conditiontype ADD VALUE IF NOT EXISTS 'ORGANIZATION'")


def downgrade() -> None:
   pass