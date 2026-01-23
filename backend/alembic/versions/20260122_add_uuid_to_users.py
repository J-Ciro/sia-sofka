"""Add UUID field to users table.

Adds UUID field as technical identifier for backend use, while keeping
the integer ID as user-friendly identifier.

Revision ID: 20260122_add_uuid
Revises: 20260119_add_fecha_especifica
Create Date: 2026-01-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision: str = "20260122_add_uuid"
down_revision: Union[str, None] = "20260119_add_fecha_especifica"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if users table exists
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()
    
    if 'users' not in existing_tables:
        print("Table 'users' does not exist. Skipping UUID column addition.")
        return
    
    # Check if column already exists
    existing_columns = [col['name'] for col in inspector.get_columns('users')]
    if 'uuid' in existing_columns:
        print("Column 'uuid' already exists. Skipping.")
        return
    
    # Add UUID column as nullable first (to allow existing rows)
    op.add_column(
        'users',
        sa.Column(
            'uuid',
            UUID(as_uuid=True),
            nullable=True,  # Temporary, will be populated and made NOT NULL
            unique=True
        )
    )
    
    # Generate UUIDs for existing users
    print("Generating UUIDs for existing users...")
    connection = op.get_bind()
    
    # Get all users without UUID
    result = connection.execute(sa.text("SELECT id FROM users WHERE uuid IS NULL"))
    user_ids = [row[0] for row in result]
    
    # Generate and assign UUIDs using SQLAlchemy Table API
    users_table = sa.table(
        'users',
        sa.column('id', sa.Integer),
        sa.column('uuid', UUID(as_uuid=True))
    )
    
    for user_id in user_ids:
        new_uuid = uuid.uuid4()
        # Use SQLAlchemy update statement for proper type handling
        update_stmt = users_table.update().where(
            users_table.c.id == user_id
        ).values(uuid=new_uuid)
        connection.execute(update_stmt)
    
    connection.commit()
    
    # Now make the column NOT NULL
    op.alter_column('users', 'uuid', nullable=False)
    
    # Add index for UUID
    op.create_index('ix_users_uuid', 'users', ['uuid'], unique=True)
    
    print("✓ UUID column added and populated for all users")


def downgrade() -> None:
    # Remove UUID index
    op.drop_index('ix_users_uuid', table_name='users')
    
    # Remove UUID column
    op.drop_column('users', 'uuid')
