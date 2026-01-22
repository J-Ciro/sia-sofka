"""Add fecha_especifica field to schedules table.

Adds optional fecha_especifica Date field to Schedule model for date-specific scheduling.
Includes new indexes and constraints for date-specific queries and data consistency.

Revision ID: 20260119_add_fecha_especifica
Revises: 20260119
Create Date: 2026-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260119_add_fecha_especifica"
down_revision: Union[str, None] = "20260119"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add fecha_especifica column to schedules table
    op.add_column('schedules', sa.Column('fecha_especifica', sa.Date(), nullable=True))
    
    # Add index for fecha_especifica field
    op.create_index('ix_schedules_fecha_especifica', 'schedules', ['fecha_especifica'], unique=False)
    
    # Add composite index for date-specific queries (classroom, fecha_especifica, hora_inicio)
    op.create_index(
        'ix_schedule_classroom_fecha_hora', 
        'schedules', 
        ['classroom_id', 'fecha_especifica', 'hora_inicio'], 
        unique=False
    )
    
    # Add unique constraint for date-specific schedules (subject_id, fecha_especifica, hora_inicio)
    # This constraint only applies when fecha_especifica is NOT NULL
    op.create_unique_constraint(
        'uq_schedule_subject_fecha_hora',
        'schedules',
        ['subject_id', 'fecha_especifica', 'hora_inicio']
    )


def downgrade() -> None:
    # Remove unique constraint
    op.drop_constraint('uq_schedule_subject_fecha_hora', 'schedules', type_='unique')
    
    # Remove composite index
    op.drop_index('ix_schedule_classroom_fecha_hora', table_name='schedules')
    
    # Remove fecha_especifica index
    op.drop_index('ix_schedules_fecha_especifica', table_name='schedules')
    
    # Remove fecha_especifica column
    op.drop_column('schedules', 'fecha_especifica')