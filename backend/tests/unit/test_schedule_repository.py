"""Unit tests for ScheduleRepository (Fase 2 - TDD). Async.

TASK-006: Solapamiento de aulas.
TASK-007: Solapamiento de profesor.
TASK-008: Solapamiento de estudiante.
TASK-009: get_weekly_schedule(user_id, role).
"""

import pytest
from datetime import time

from app.models.schedule import Classroom, Schedule
from app.models.user import UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.repositories.schedule_repository import ScheduleRepository


@pytest.fixture
def schedule_repo(async_db_session):
    return ScheduleRepository(async_db_session)


class TestFindClassroomOverlaps:
    """TASK-006: query de solapamiento de aulas."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_classroom_overlap_exact(
        self, async_db_session, async_subject, async_classroom, schedule_repo
    ):
        """Solapamiento exacto: mismo aula, mismo día, mismo rango."""
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        overlaps = await schedule_repo.find_classroom_overlaps(
            async_classroom.id, 1, time(8, 0), time(10, 0)
        )
        assert len(overlaps) == 1
        assert overlaps[0].hora_inicio == time(8, 0)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_classroom_overlap_partial(
        self, async_db_session, async_subject, async_classroom, schedule_repo
    ):
        """Solapamiento parcial: nuevo 09:00-11:00 vs existente 08:00-10:00."""
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        overlaps = await schedule_repo.find_classroom_overlaps(
            async_classroom.id, 1, time(9, 0), time(11, 0)
        )
        assert len(overlaps) == 1
        assert overlaps[0].hora_inicio == time(8, 0)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_no_classroom_overlap_consecutive(
        self, async_db_session, async_subject, async_classroom, schedule_repo
    ):
        """Horarios consecutivos 08-10 y 10-12 no solapan."""
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        overlaps = await schedule_repo.find_classroom_overlaps(
            async_classroom.id, 1, time(10, 0), time(12, 0)
        )
        assert len(overlaps) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_exclude_schedule_id_on_update(
        self, async_db_session, async_subject, async_classroom, schedule_repo
    ):
        """Al editar, excluir el propio horario de la búsqueda de solapamiento."""
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        overlaps = await schedule_repo.find_classroom_overlaps(
            async_classroom.id, 1, time(8, 0), time(10, 0), exclude_schedule_id=s.id
        )
        assert len(overlaps) == 0


class TestFindProfessorOverlaps:
    """TASK-007: query de solapamiento de profesor."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_professor_overlap(
        self,
        async_db_session,
        async_subject,
        async_subject2,
        async_classroom,
        async_classroom2,
        async_profesor_user,
        schedule_repo,
    ):
        """Mismo profesor, dos materias, horarios que se solapan."""
        s1 = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        s2 = Schedule(
            subject_id=async_subject2.id,
            classroom_id=async_classroom2.id,
            dia_semana=1,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        async_db_session.add_all([s1, s2])
        await async_db_session.commit()
        overlaps = await schedule_repo.find_professor_overlaps(
            async_profesor_user.id, 1, time(9, 0), time(10, 0)
        )
        assert len(overlaps) == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_no_professor_overlap_different_days(
        self, async_db_session, async_subject, async_classroom, async_profesor_user, schedule_repo
    ):
        """Mismo profesor, distintos días: no conflicto."""
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        overlaps = await schedule_repo.find_professor_overlaps(
            async_profesor_user.id, 2, time(8, 0), time(10, 0)
        )
        assert len(overlaps) == 0


class TestFindStudentOverlaps:
    """TASK-008: query de solapamiento de estudiante."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_student_overlap(
        self,
        async_db_session,
        async_subject,
        async_subject2,
        async_classroom,
        async_classroom2,
        async_estudiante_user,
        async_enrollment,
        async_enrollment2,
        schedule_repo,
    ):
        """Estudiante inscrito en 2 materias con horarios que se solapan."""
        s1 = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        s2 = Schedule(
            subject_id=async_subject2.id,
            classroom_id=async_classroom2.id,
            dia_semana=1,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        async_db_session.add_all([s1, s2])
        await async_db_session.commit()
        overlaps = await schedule_repo.find_student_overlaps(
            async_estudiante_user.id, 1, time(9, 0), time(10, 0)
        )
        assert len(overlaps) == 2


class TestGetWeeklySchedule:
    """TASK-009: get_weekly_schedule(user_id, role)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_professor_weekly_schedule(
        self, async_db_session, async_subject, async_classroom, async_profesor_user, schedule_repo
    ):
        """Profesor ve sus horarios (materias que imparte)."""
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        rows = await schedule_repo.get_weekly_schedule(async_profesor_user.id, UserRole.PROFESOR)
        assert len(rows) == 1
        assert rows[0].subject.nombre == "Matemáticas Avanzadas"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_student_weekly_schedule(
        self, async_db_session, async_subject, async_classroom, async_estudiante_user, async_enrollment, schedule_repo
    ):
        """Estudiante ve horarios de materias en las que está inscrito."""
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        async_db_session.add(s)
        await async_db_session.commit()
        rows = await schedule_repo.get_weekly_schedule(async_estudiante_user.id, UserRole.ESTUDIANTE)
        assert len(rows) == 1
        assert rows[0].subject.nombre == "Matemáticas Avanzadas"
