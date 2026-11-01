"""Add org permissions

Revision ID: d109c33f7ea3
Revises: cc0f9b78035e
Create Date: 2026-11-01 16:22:39.321041

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd109c33f7ea3'
down_revision: Union[str, Sequence[str], None] = 'cc0f9b78035e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



CHECK_CONSTRAINT_NEW = """
(type = 'ALL'          AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NULL AND organization_id IS NULL) OR
(type = 'CATEGORY'     AND category_id IS NOT NULL AND role_id IS NULL AND media_type_id IS NULL AND organization_id IS NULL) OR
(type = 'ROLE'         AND role_id IS NOT NULL AND category_id IS NULL AND media_type_id IS NULL AND organization_id IS NULL) OR
(type = 'CREATOR'      AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NULL AND organization_id IS NULL) OR
(type = 'SUBTREE'      AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NULL AND organization_id IS NULL) OR
(type = 'MEDIA'        AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NOT NULL AND organization_id IS NULL) OR
(type = 'ORGANIZATION' AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NULL AND organization_id IS NOT NULL)
"""

CHECK_CONSTRAINT_OLD = """
(type = 'ALL'      AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NULL) OR
(type = 'CATEGORY' AND category_id IS NOT NULL AND role_id IS NULL AND media_type_id IS NULL) OR
(type = 'ROLE'     AND role_id IS NOT NULL AND category_id IS NULL AND media_type_id IS NULL) OR
(type = 'CREATOR'  AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NULL) OR
(type = 'SUBTREE'  AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NULL) OR
(type = 'MEDIA'    AND category_id IS NULL AND role_id IS NULL AND media_type_id IS NOT NULL)
"""


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Новая колонка
    op.add_column(
        'permission_conditions',
        sa.Column('organization_id', sa.UUID(), nullable=True),
    )

    # 2. Старые constraints
    op.drop_constraint(
        'uq_permission_condition',
        'permission_conditions',
        type_='unique',
    )
    op.drop_constraint(
        'ck_permission_condition_type',
        'permission_conditions',
        type_='check',
    )

    # 3. Новые constraints
    op.create_unique_constraint(
        'uq_permission_condition',
        'permission_conditions',
        [
            'permission_id',
            'type',
            'category_id',
            'role_id',
            'media_type_id',
            'organization_id',
        ],
        postgresql_nulls_not_distinct=True,
    )
    op.create_check_constraint(
        'ck_permission_condition_type',
        'permission_conditions',
        CHECK_CONSTRAINT_NEW,
    )

    # 4. FK на organizations
    op.create_foreign_key(
        'fk_permission_conditions_organization_id',
        'permission_conditions',
        'organizations',
        ['organization_id'],
        ['id'],
        ondelete='CASCADE',
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 1. FK
    op.drop_constraint(
        'fk_permission_conditions_organization_id',
        'permission_conditions',
        type_='foreignkey',
    )

    # 2. Новые constraints
    op.drop_constraint(
        'uq_permission_condition',
        'permission_conditions',
        type_='unique',
    )
    op.drop_constraint(
        'ck_permission_condition_type',
        'permission_conditions',
        type_='check',
    )

    # 3. Старые constraints
    op.create_unique_constraint(
        'uq_permission_condition',
        'permission_conditions',
        [
            'permission_id',
            'type',
            'category_id',
            'role_id',
            'media_type_id',
        ],
        postgresql_nulls_not_distinct=True,
    )
    op.create_check_constraint(
        'ck_permission_condition_type',
        'permission_conditions',
        CHECK_CONSTRAINT_OLD,
    )

    # 4. Колонка
    op.drop_column('permission_conditions', 'organization_id')