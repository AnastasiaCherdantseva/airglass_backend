"""add forbidden permission combinations check

Revision ID: 6ae6e0228da2
Revises: 40da66ebb2c9
Create Date: 2026-09-28 23:14:57.339231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ae6e0228da2'
down_revision: Union[str, Sequence[str], None] = '40da66ebb2c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add check constraint for forbidden permission combinations."""
    op.create_check_constraint(
        'ck_permission_forbidden_combinations',
        'permissions',
        """
        NOT (
            (resource = 'USERS'      AND action = 'ARCHIVE') OR
            (resource = 'PROJECTS'   AND action IN ('IMPORT', 'EXPORT')) OR
            (resource = 'CUSTOMERS'  AND action = 'ARCHIVE') OR
            (resource = 'MEDIA'      AND action IN ('ARCHIVE', 'EXPORT', 'IMPORT')) OR
            (resource = 'CALCULATOR' AND action IN ('ARCHIVE', 'IMPORT')) OR
            (resource = 'SETTINGS'   AND action IN ('CREATE', 'DELETE', 'ARCHIVE', 'EXPORT', 'IMPORT')) OR
            (resource = 'AUDIT_LOG'  AND action IN ('CREATE', 'UPDATE', 'DELETE', 'ARCHIVE', 'IMPORT'))
        )
        """,
    )


def downgrade() -> None:
    """Drop check constraint for forbidden permission combinations."""
    op.drop_constraint(
        'ck_permission_forbidden_combinations',
        'permissions',
        type_='check',
    )
