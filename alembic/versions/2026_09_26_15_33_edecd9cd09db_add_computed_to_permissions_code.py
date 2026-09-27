"""add computed to permissions.code

Revision ID: edecd9cd09db
Revises: b3d85c09b35d
Create Date: 2026-09-26 15:33:42.280624

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edecd9cd09db'
down_revision: Union[str, Sequence[str], None] = 'b3d85c09b35d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
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
    # 1. Снять уникальность со старой колонки code
    op.execute("""
        ALTER TABLE permissions
        DROP CONSTRAINT IF EXISTS permissions_code_key
    """)
    op.execute("""
        ALTER TABLE permissions
        DROP CONSTRAINT IF EXISTS uq_permissions_code
    """)
    op.execute("DROP INDEX IF EXISTS permissions_code_key")
    op.execute("DROP INDEX IF EXISTS uq_permissions_code")

    # 2. Удалить колонку code, если существует
    op.execute("ALTER TABLE permissions DROP COLUMN IF EXISTS code")

    # 3. Создать колонку с GENERATED ALWAYS AS
    #    Postgres сам заполнит её для всех существующих строк
    op.execute("""
        ALTER TABLE permissions
        ADD COLUMN code VARCHAR(150)
        GENERATED ALWAYS AS (permission_code(resource, action)) STORED
        NOT NULL
    """)
    # 4. Вернуть уникальность
    op.create_unique_constraint("uq_permissions_code", "permissions", ["code"])


def downgrade() -> None:
    """Downgrade schema."""
    # 1. Снять уникальность
    op.execute("""
            ALTER TABLE permissions
            DROP CONSTRAINT IF EXISTS uq_permissions_code
        """)
    op.execute("DROP INDEX IF EXISTS uq_permissions_code")
    # 2. Удалить колонку code, если существует
    op.execute("ALTER TABLE permissions DROP COLUMN IF EXISTS code")
    # 3. Создать колонку
    op.execute("ALTER TABLE permissions ADD COLUMN code VARCHAR(150)")
     # 4. Заполнить значениями (Postgres сам не заполнит — колонка не GENERATED)
    op.execute("""
        UPDATE permissions
        SET code = resource::text || '.' || action::text
    """)
    # 5. NOT NULL + UNIQUE
    op.execute("ALTER TABLE permissions ALTER COLUMN code SET NOT NULL")
    op.create_unique_constraint("permissions_code_key", "permissions", ["code"])
    op.execute("DROP FUNCTION IF EXISTS permission_code(permissionresource, permissionaction)")

    
