"""add ORGANIZATIONS to permission zone check

Revision ID: a36ab9b3bccd
Revises: d109c33f7ea3
Create Date: 2026-11-01 16:30:33.623554

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a36ab9b3bccd'
down_revision: Union[str, Sequence[str], None] = 'd109c33f7ea3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



CHECK_NEW = """
(resource IN ('USERS', 'ROLES', 'ORGANIZATIONS', 'PROJECTS', 'CUSTOMERS', 'CALCULATOR', 'MEDIA')
    AND zone = 'PUBLIC') OR
(resource IN ('PRODUCTS', 'CATEGORIES', 'TEMPLATES', 'SUPPLIERS', 'SETTINGS', 'AUDIT_LOG')
    AND zone = 'ADMIN')
"""

CHECK_OLD = """
(resource IN ('USERS', 'ROLES', 'PROJECTS', 'CUSTOMERS', 'CALCULATOR', 'MEDIA')
    AND zone = 'PUBLIC') OR
(resource IN ('PRODUCTS', 'CATEGORIES', 'TEMPLATES', 'SUPPLIERS', 'SETTINGS', 'AUDIT_LOG')
    AND zone = 'ADMIN')
"""

def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint(
        'ck_permission_zone_by_resource',
        'permissions',
        type_='check',
    )
    op.create_check_constraint(
        'ck_permission_zone_by_resource',
        'permissions',
        CHECK_NEW,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        'ck_permission_zone_by_resource',
        'permissions',
        type_='check',
    )
    op.create_check_constraint(
        'ck_permission_zone_by_resource',
        'permissions',
        CHECK_OLD,
    )
