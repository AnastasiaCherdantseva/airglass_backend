"""remove QUOTES from permissionresource enum

Revision ID: 40da66ebb2c9
Revises: 8eb95ca4ce32
Create Date: 2026-09-28 23:22:05.295739

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40da66ebb2c9'
down_revision: Union[str, Sequence[str], None] = '8eb95ca4ce32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
def upgrade() -> None:
    """Recreate permissionresource enum without QUOTES."""
    # 1. Снять generated column
    op.execute("ALTER TABLE permissions DROP COLUMN code")

    # 2. Удалить функцию permission_code (она зависит от типа permissionresource)
    op.execute("DROP FUNCTION permission_code(permissionresource, permissionaction)")

    # 3. Создать новый тип без QUOTES
    op.execute("""
        CREATE TYPE permissionresource_new AS ENUM (
            'USERS', 'ROLES', 'PRODUCTS', 'CATEGORIES', 'TEMPLATES',
            'PROJECTS', 'CUSTOMERS', 'SUPPLIERS', 'MEDIA', 'CALCULATOR',
            'SETTINGS', 'AUDIT_LOG'
        )
    """)

    # 4. Перевести колонку resource на новый тип
    op.execute("""
        ALTER TABLE permissions
        ALTER COLUMN resource TYPE permissionresource_new
        USING resource::text::permissionresource_new
    """)

    # 5. Удалить старый тип и переименовать новый
    op.execute("DROP TYPE permissionresource")
    op.execute("ALTER TYPE permissionresource_new RENAME TO permissionresource")

    # 6. Пересоздать функцию permission_code с новым типом
    op.execute("""
         CREATE OR REPLACE FUNCTION permission_code(
                    resource permissionresource,
                    action permissionaction
                )
                RETURNS text
                LANGUAGE sql
                IMMUTABLE
                AS $$
                    SELECT resource::text || '.' || action::text;
                $$;
    """)

    # 7. Вернуть generated column code
    op.execute("""
        ALTER TABLE permissions
        ADD COLUMN code VARCHAR(150)
        GENERATED ALWAYS AS (permission_code(resource, action)) STORED
    """)

    # 8. Вернуть unique на code
    op.execute("ALTER TABLE permissions ADD CONSTRAINT permissions_code_key UNIQUE (code)")


def downgrade() -> None:
    """Recreate permissionresource enum with QUOTES."""
    op.execute("ALTER TABLE permissions DROP COLUMN code")
    op.execute("DROP FUNCTION permission_code(permissionresource, permissionaction)")

    op.execute("""
        CREATE TYPE permissionresource_new AS ENUM (
            'USERS', 'ROLES', 'PRODUCTS', 'CATEGORIES', 'TEMPLATES',
            'QUOTES',
            'PROJECTS', 'CUSTOMERS', 'SUPPLIERS', 'MEDIA', 'CALCULATOR',
            'SETTINGS', 'AUDIT_LOG'
        )
    """)

    op.execute("""
        ALTER TABLE permissions
        ALTER COLUMN resource TYPE permissionresource_new
        USING resource::text::permissionresource_new
    """)

    op.execute("DROP TYPE permissionresource")
    op.execute("ALTER TYPE permissionresource_new RENAME TO permissionresource")

    op.execute("""
         CREATE OR REPLACE FUNCTION permission_code(
                    resource permissionresource,
                    action permissionaction
                )
                RETURNS text
                LANGUAGE sql
                IMMUTABLE
                AS $$
                    SELECT resource::text || '.' || action::text;
                $$;
    """)

    op.execute("""
        ALTER TABLE permissions
        ADD COLUMN code VARCHAR(150)
        GENERATED ALWAYS AS (permission_code(resource, action)) STORED
    """)

    op.execute("ALTER TABLE permissions ADD CONSTRAINT permissions_code_key UNIQUE (code)")