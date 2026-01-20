"""Unit tests for ScheduleService (Fase 3 - TDD). Async.

TASK-010: validate_schedule_conflicts
TASK-011: detección de solapamiento
TASK-012: get_professor_schedule
TASK-013: get_student_schedule
"""

import pytest
from datetime import time

from app.models.schedule import Classroom, Schedule
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.services.schedule_service import ScheduleService


@pytest.fixture
def schedule_service(async_db_session):
    return ScheduleService(async_db_session)


class TestValidateScheduleConflicts:
    """TASK-010, TASK-011."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_schedule_conflicts_sin_conflictos(
        self, async_subject, async_classroom, schedule_service
    ):
        """Sin horarios existentes no hay conflictos."""
        conflicts = await schedule_service.validate_schedule_conflicts(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        assert conflicts == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_schedule_conflicts_conflicto_aula(
        self, async_db_session, async_subject, async_subject2, async_classroom, schedule_service
    ):
        """Aula ocupada en mismo día y rango solapado."""
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        conflicts = await schedule_service.validate_schedule_conflicts(
            subject_id=async_subject2.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        types = [c["type"] for c in conflicts]
        assert "classroom" in types

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_schedule_conflicts_conflicto_profesor(
        self,
        async_db_session,
        async_subject,
        async_subject2,
        async_classroom,
        async_classroom2,
        async_profesor_user,
        schedule_service,
    ):
        """Mismo profesor en dos aulas a la misma hora."""
        s1 = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s1)
        await async_db_session.commit()
        conflicts = await schedule_service.validate_schedule_conflicts(
            subject_id=async_subject2.id,
            classroom_id=async_classroom2.id,
            dia_semana=1,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        types = [c["type"] for c in conflicts]
        assert "professor" in types

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_schedule_conflicts_exclude_en_edicion(
        self, async_db_session, async_subject, async_classroom, schedule_service
    ):
        """Al editar, excluir el propio horario: no debe dar conflicto consigo mismo."""
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        conflicts = await schedule_service.validate_schedule_conflicts(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            exclude_schedule_id=s.id,
        )
        assert conflicts == []


class TestGetProfessorSchedule:
    """TASK-012."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_professor_schedule(
        self, async_db_session, async_subject, async_classroom, async_profesor_user, schedule_service
    ):
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        rows = await schedule_service.get_professor_schedule(async_profesor_user.id)
        assert len(rows) == 1
        assert rows[0].subject.nombre == "Matemáticas Avanzadas"


class TestGetStudentSchedule:
    """TASK-013."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_student_schedule(
        self, async_db_session, async_subject, async_classroom, async_estudiante_user, async_enrollment, schedule_service
    ):
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        rows = await schedule_service.get_student_schedule(async_estudiante_user.id)
        assert len(rows) == 1
        assert rows[0].subject.nombre == "Matemáticas Avanzadas"
