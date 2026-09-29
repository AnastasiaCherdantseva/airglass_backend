"""add zone column to permissions

Revision ID: 01a409a18cd2
Revises: 6ae6e0228da2
Create Date: 2026-09-29 00:41:55.439487

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '01a409a18cd2'
down_revision: Union[str, Sequence[str], None] = '6ae6e0228da2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade() -> None:
    """Add zone column to permissions."""
    permission_zone = sa.Enum('PUBLIC', 'ADMIN', name='permission_zone')
    permission_zone.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'permissions',
        sa.Column(
            'zone',
            permission_zone,
            nullable=False,
            server_default='PUBLIC',
        ),
    )
    op.alter_column('permissions', 'zone', server_default=None)
    op.execute("""
        UPDATE permissions SET zone = 'ADMIN'
        WHERE resource IN ('PRODUCTS', 'CATEGORIES', 'TEMPLATES', 'SUPPLIERS', 'SETTINGS', 'AUDIT_LOG')
    """)
    op.execute("""
        UPDATE permissions SET zone = 'PUBLIC'
        WHERE resource IN ('USERS', 'ROLES', 'PROJECTS', 'CUSTOMERS', 'CALCULATOR', 'MEDIA')
    """)
    op.create_check_constraint(
        'ck_permission_zone_by_resource',
        'permissions',
        """
        (resource IN ('USERS', 'ROLES', 'PROJECTS', 'CUSTOMERS', 'CALCULATOR', 'MEDIA')
            AND zone = 'PUBLIC') OR
        (resource IN ('PRODUCTS', 'CATEGORIES', 'TEMPLATES', 'SUPPLIERS', 'SETTINGS', 'AUDIT_LOG')
            AND zone = 'ADMIN')
        """,
    )


def downgrade() -> None:
    """Drop zone column from permissions."""
    op.drop_constraint('ck_permission_zone_by_resource', 'permissions', type_='check')
    op.drop_column('permissions', 'zone')
    sa.Enum(name='permission_zone').drop(op.get_bind(), checkfirst=True)