"""modify access tables

Revision ID: 0ab8b0b28c57
Revises: 1b1bbffe73e8
Create Date: 2026-09-21 17:20:14.237728

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0ab8b0b28c57'
down_revision: Union[str, Sequence[str], None] = '1b1bbffe73e8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    """Upgrade schema."""
    # 1. Создать enum-типы
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE conditiontype AS ENUM ('ALL', 'CATEGORY', 'ROLE', 'CREATOR');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)
    
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE permission_effect AS ENUM ('ALLOW', 'DENY');
        EXCEPTION WHEN duplicate_object THEN null;
        END $$;
    """)

    # 2. Создать user_direct_permissions
    op.create_table('user_direct_permissions',
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('condition_id', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['condition_id'], ['permission_conditions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'condition_id')
    )
    op.create_index('ix_user_direct_permission_condition_id', 'user_direct_permissions', ['condition_id'], unique=False)

    # 3. Изменить permission_conditions
    op.add_column('permission_conditions', sa.Column('effect', postgresql.ENUM('ALLOW', 'DENY', name='permission_effect', create_type=False), server_default=sa.text("'ALLOW'"), nullable=False))
    op.add_column('permission_conditions', sa.Column('category_id', sa.UUID(), nullable=True))
    op.add_column('permission_conditions', sa.Column('role_id', sa.UUID(), nullable=True))
    op.add_column('permission_conditions', sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    
    op.alter_column('permission_conditions', 'type',
               existing_type=postgresql.ENUM('ROLE', 'CATEGORY', 'CREATOR', 'CUSTOM', name='permissionconditiontype'),
               type_=postgresql.ENUM('ALL', 'CATEGORY', 'ROLE', 'CREATOR', name='conditiontype', create_type=False),
               existing_nullable=False,
               postgresql_using="type::text::conditiontype")
    
    op.create_unique_constraint('uq_permission_condition', 'permission_conditions', ['permission_id', 'type', 'effect', 'category_id', 'role_id'])
    op.create_foreign_key('fk_permission_conditions_role_id', 'permission_conditions', 'roles', ['role_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_permission_conditions_category_id', 'permission_conditions', 'categories', ['category_id'], ['id'], ondelete='CASCADE')
    op.drop_column('permission_conditions', 'value')
    op.drop_column('permission_conditions', 'description')

    # 4. Изменить permissions
    op.drop_index(op.f('ix_permission_code'), table_name='permissions')
    op.drop_column('permissions', 'is_active')
    op.drop_column('permissions', 'created_at')
    op.drop_column('permissions', 'scope')
    op.drop_column('permissions', 'updated_at')

    # 5. Изменить role_permissions
    op.drop_constraint('role_permissions_pkey', 'role_permissions', type_='primary')
    op.add_column('role_permissions', sa.Column('condition_id', sa.UUID(), nullable=False))
    op.drop_index(op.f('ix_role_permission_permission_id'), table_name='role_permissions')
    op.drop_constraint(op.f('uq_role_permission'), 'role_permissions', type_='unique')
    op.drop_constraint(op.f('role_permissions_permission_id_fkey'), 'role_permissions', type_='foreignkey')
    op.create_foreign_key('fk_role_permissions_condition_id', 'role_permissions', 'permission_conditions', ['condition_id'], ['id'], ondelete='CASCADE')
    op.drop_column('role_permissions', 'permission_id')
    op.drop_column('role_permissions', 'created_at')
    op.drop_column('role_permissions', 'id')
    op.create_primary_key('role_permissions_pkey', 'role_permissions', ['role_id', 'condition_id'])

    # 6. Изменить user_permissions
    op.drop_constraint('user_permissions_pkey', 'user_permissions', type_='primary')
    op.add_column('user_permissions', sa.Column('condition_id', sa.UUID(), nullable=False))
    op.drop_index('ix_user_permission_user_id', table_name='user_permissions')
    op.drop_constraint(op.f('uq_user_permission'), 'user_permissions', type_='unique')
    op.create_index('ix_user_permission_condition_id', 'user_permissions', ['condition_id'], unique=False)
    op.drop_constraint(op.f('user_permissions_permission_id_fkey'), 'user_permissions', type_='foreignkey')
    op.create_foreign_key('fk_user_permissions_condition_id', 'user_permissions', 'permission_conditions', ['condition_id'], ['id'], ondelete='CASCADE')
    op.drop_column('user_permissions', 'permission_id')
    op.drop_column('user_permissions', 'granted')
    op.drop_column('user_permissions', 'created_at')
    op.drop_column('user_permissions', 'id')
    op.create_primary_key('user_permissions_pkey', 'user_permissions', ['user_id', 'condition_id'])

def downgrade() -> None:
    """Downgrade schema."""
    # 1. Восстановить user_permissions
    op.drop_constraint('user_permissions_pkey', 'user_permissions', type_='primary')
    op.add_column('user_permissions', sa.Column('id', sa.UUID(), autoincrement=False, nullable=False))
    op.add_column('user_permissions', sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False))
    op.add_column('user_permissions', sa.Column('granted', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column('user_permissions', sa.Column('permission_id', sa.UUID(), autoincrement=False, nullable=False))
    op.drop_constraint('fk_user_permissions_condition_id', 'user_permissions', type_='foreignkey')
    op.create_foreign_key(
        op.f('user_permissions_permission_id_fkey'),
        'user_permissions', 'permissions',
        ['permission_id'], ['id'],
        ondelete='CASCADE',
    )
    op.drop_index('ix_user_permission_condition_id', table_name='user_permissions')
    op.create_unique_constraint(op.f('uq_user_permission'), 'user_permissions', ['user_id', 'permission_id'])
    op.drop_column('user_permissions', 'condition_id')
    op.create_primary_key('user_permissions_pkey', 'user_permissions', ['id'])
    op.create_index('ix_user_permission_user_id', 'user_permissions', ['user_id'], unique=False)

    # 2. Восстановить role_permissions
    op.drop_constraint('role_permissions_pkey', 'role_permissions', type_='primary')
    op.add_column('role_permissions', sa.Column('id', sa.UUID(), autoincrement=False, nullable=False))
    op.add_column('role_permissions', sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False))
    op.add_column('role_permissions', sa.Column('permission_id', sa.UUID(), autoincrement=False, nullable=False))
    op.drop_constraint('fk_role_permissions_condition_id', 'role_permissions', type_='foreignkey')
    op.create_foreign_key(
        op.f('role_permissions_permission_id_fkey'),
        'role_permissions', 'permissions',
        ['permission_id'], ['id'],
        ondelete='CASCADE',
    )
    op.create_unique_constraint(op.f('uq_role_permission'), 'role_permissions', ['role_id', 'permission_id'])
    op.create_index(op.f('ix_role_permission_permission_id'), 'role_permissions', ['permission_id'], unique=False)
    op.drop_column('role_permissions', 'condition_id')
    op.create_primary_key('role_permissions_pkey', 'role_permissions', ['id'])

    # 3. Восстановить permissions
    op.add_column('permissions', sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False))
    op.add_column('permissions', sa.Column('scope', postgresql.ENUM('ALL', 'OWN', 'DEPARTMENT', 'ASSIGNED', 'SPECIFIC', name='permissionscope'), autoincrement=False, nullable=False))
    op.add_column('permissions', sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False))
    op.add_column('permissions', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.create_index(op.f('ix_permission_code'), 'permissions', ['code'], unique=False)

    # 4. Восстановить permission_conditions
    op.add_column('permission_conditions', sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('permission_conditions', sa.Column('value', sa.VARCHAR(length=255), autoincrement=False, nullable=False))

    op.drop_constraint('fk_permission_conditions_role_id', 'permission_conditions', type_='foreignkey')
    op.drop_constraint('fk_permission_conditions_category_id', 'permission_conditions', type_='foreignkey')
    op.drop_constraint('uq_permission_condition', 'permission_conditions', type_='unique')

    op.alter_column('permission_conditions', 'type',
               existing_type=postgresql.ENUM('ALL', 'CATEGORY', 'ROLE', 'CREATOR', name='conditiontype', create_type=False),
               type_=postgresql.ENUM('ROLE', 'CATEGORY', 'CREATOR', 'CUSTOM', name='permissionconditiontype', create_type=False),
               existing_nullable=False,
               postgresql_using="type::text::permissionconditiontype")

    op.drop_column('permission_conditions', 'is_active')
    op.drop_column('permission_conditions', 'role_id')
    op.drop_column('permission_conditions', 'category_id')
    op.drop_column('permission_conditions', 'effect')

    # 5. Удалить user_direct_permissions
    op.drop_index('ix_user_direct_permission_condition_id', table_name='user_direct_permissions')
    op.drop_table('user_direct_permissions')

    # 6. Удалить созданные enum
    op.execute("DROP TYPE IF EXISTS permission_effect")
    op.execute("DROP TYPE IF EXISTS conditiontype")
    """Downgrade schema."""
  