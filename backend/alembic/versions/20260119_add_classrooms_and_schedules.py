"""Add classrooms and schedules tables (Fase 1 - horarios-calendario).

TASK-001: Classroom (aula) con capacidad y ubicación.
TASK-002: Schedule con asignatura, aula, día, hora_inicio, hora_fin.
TASK-003: Unique (subject_id, dia_semana, hora_inicio).
TASK-004: Índice (classroom_id, dia_semana, hora_inicio).

Revision ID: 20260119
Revises: None
Create Date: 2026-01-19

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260119"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if tables already exist (created by Base.metadata.create_all)
    from sqlalchemy import inspect
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()
    
    if "classrooms" not in existing_tables:
        op.create_table(
            "classrooms",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("codigo", sa.String(), nullable=False),
            sa.Column("nombre", sa.String(), nullable=False),
            sa.Column("capacidad", sa.Integer(), nullable=False),
            sa.Column("ubicacion", sa.String(), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_classrooms_id", "classrooms", ["id"], unique=False)
        op.create_index("ix_classrooms_codigo", "classrooms", ["codigo"], unique=True)
    else:
        print("Table 'classrooms' already exists, skipping creation")

    if "schedules" not in existing_tables:
        # Verify that subjects table exists before creating schedules
        if "subjects" not in existing_tables:
            raise Exception("Cannot create 'schedules' table: 'subjects' table does not exist. Please ensure all base tables are created first.")
        
        op.create_table(
            "schedules",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("codigo", sa.String(), nullable=False),
            sa.Column("subject_id", sa.Integer(), nullable=False),
            sa.Column("classroom_id", sa.Integer(), nullable=False),
            sa.Column("dia_semana", sa.Integer(), nullable=False),
            sa.Column("hora_inicio", sa.Time(), nullable=False),
            sa.Column("hora_fin", sa.Time(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(),
                server_default=sa.func.now(),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["classroom_id"], ["classrooms.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "subject_id",
                "dia_semana",
                "hora_inicio",
                name="uq_schedule_subject_dia_hora",
            ),
        )
        op.create_index("ix_schedules_id", "schedules", ["id"], unique=False)
        op.create_index("ix_schedules_codigo", "schedules", ["codigo"], unique=True)
        op.create_index("ix_schedules_subject_id", "schedules", ["subject_id"], unique=False)
        op.create_index("ix_schedules_classroom_id", "schedules", ["classroom_id"], unique=False)
        op.create_index("ix_schedules_dia_semana", "schedules", ["dia_semana"], unique=False)
        op.create_index(
            "ix_schedule_classroom_dia_hora",
            "schedules",
            ["classroom_id", "dia_semana", "hora_inicio"],
            unique=False,
        )
    else:
        print("Table 'schedules' already exists, skipping creation")


def downgrade() -> None:
    op.drop_index("ix_schedule_classroom_dia_hora", table_name="schedules")
    op.drop_index("ix_schedules_dia_semana", table_name="schedules")
    op.drop_index("ix_schedules_classroom_id", table_name="schedules")
    op.drop_index("ix_schedules_subject_id", table_name="schedules")
    op.drop_index("ix_schedules_codigo", table_name="schedules")
    op.drop_index("ix_schedules_id", table_name="schedules")
    op.drop_table("schedules")

    op.drop_index("ix_classrooms_codigo", table_name="classrooms")
    op.drop_index("ix_classrooms_id", table_name="classrooms")
    op.drop_table("classrooms")
