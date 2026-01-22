"""Unit tests for ScheduleRepository (Fase 2 - TDD). Async.

TASK-006: Solapamiento de aulas.
TASK-007: Solapamiento de profesor.
TASK-008: Solapamiento de estudiante.
TASK-009: get_weekly_schedule(user_id, role).
TASK-3.1: Date-specific conflict detection and date range queries.
"""

import pytest
from datetime import time, date

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


class TestFindClassroomOverlapsByDate:
    """TASK-3.1: Date-specific classroom conflict detection."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_classroom_overlap_by_date(
        self, async_db_session, async_subject, async_classroom, schedule_repo
    ):
        """Date-specific classroom overlap detection."""
        specific_date = date(2024, 1, 15)  # Monday
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,  # Monday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=specific_date,
        )
        async_db_session.add(s)
        await async_db_session.commit()
        
        # Check for overlap on the same date
        overlaps = await schedule_repo.find_classroom_overlaps_by_date(
            async_classroom.id, specific_date, time(9, 0), time(11, 0)
        )
        assert len(overlaps) == 1
        assert overlaps[0].fecha_especifica == specific_date

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_no_classroom_overlap_different_date(
        self, async_db_session, async_subject, async_classroom, schedule_repo
    ):
        """No overlap when checking different dates."""
        specific_date = date(2024, 1, 15)  # Monday
        different_date = date(2024, 1, 22)  # Different Monday
        
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,  # Monday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=specific_date,
        )
        async_db_session.add(s)
        await async_db_session.commit()
        
        # Check for overlap on different date
        overlaps = await schedule_repo.find_classroom_overlaps_by_date(
            async_classroom.id, different_date, time(8, 0), time(10, 0)
        )
        assert len(overlaps) == 0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_exclude_schedule_id_by_date(
        self, async_db_session, async_subject, async_classroom, schedule_repo
    ):
        """Exclude specific schedule ID from date-based conflict check."""
        specific_date = date(2024, 1, 15)  # Monday
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,  # Monday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=specific_date,
        )
        async_db_session.add(s)
        await async_db_session.commit()
        
        # Check for overlap excluding the same schedule
        overlaps = await schedule_repo.find_classroom_overlaps_by_date(
            async_classroom.id, specific_date, time(8, 0), time(10, 0), exclude_schedule_id=s.id
        )
        assert len(overlaps) == 0


class TestFindProfessorOverlapsByDate:
    """TASK-3.1: Date-specific professor conflict detection."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_detect_professor_overlap_by_date(
        self,
        async_db_session,
        async_subject,
        async_subject2,
        async_classroom,
        async_classroom2,
        async_profesor_user,
        schedule_repo,
    ):
        """Date-specific professor overlap detection."""
        specific_date = date(2024, 1, 15)  # Monday
        
        s1 = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,  # Monday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=specific_date,
        )
        s2 = Schedule(
            subject_id=async_subject2.id,
            classroom_id=async_classroom2.id,
            dia_semana=1,  # Monday
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
            fecha_especifica=specific_date,
        )
        async_db_session.add_all([s1, s2])
        await async_db_session.commit()
        
        # Check for professor overlap on specific date
        overlaps = await schedule_repo.find_professor_overlaps_by_date(
            async_profesor_user.id, specific_date, time(9, 0), time(10, 0)
        )
        assert len(overlaps) == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_no_professor_overlap_different_date(
        self, async_db_session, async_subject, async_classroom, async_profesor_user, schedule_repo
    ):
        """No professor overlap when checking different dates."""
        specific_date = date(2024, 1, 15)  # Monday
        different_date = date(2024, 1, 22)  # Different Monday
        
        s = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,  # Monday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=specific_date,
        )
        async_db_session.add(s)
        await async_db_session.commit()
        
        # Check for overlap on different date
        overlaps = await schedule_repo.find_professor_overlaps_by_date(
            async_profesor_user.id, different_date, time(8, 0), time(10, 0)
        )
        assert len(overlaps) == 0


class TestGetSchedulesByDateRange:
    """TASK-3.1: Date range queries for calendar display."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_schedules_by_date_range_date_specific(
        self, async_db_session, async_subject, async_classroom, schedule_repo
    ):
        """Get date-specific schedules within range."""
        date1 = date(2024, 1, 15)  # Monday
        date2 = date(2024, 1, 17)  # Wednesday
        date3 = date(2024, 1, 25)  # Outside range
        
        s1 = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,  # Monday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=date1,
        )
        s2 = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=3,  # Wednesday
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            fecha_especifica=date2,
        )
        s3 = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,  # Monday
            hora_inicio=time(14, 0),
            hora_fin=time(16, 0),
            fecha_especifica=date3,  # Outside range
        )
        async_db_session.add_all([s1, s2, s3])
        await async_db_session.commit()
        
        # Query for range that includes date1 and date2 but not date3
        schedules = await schedule_repo.get_schedules_by_date_range(
            date(2024, 1, 14), date(2024, 1, 20)
        )
        
        # Should get s1 and s2, but not s3
        date_specific_schedules = [s for s in schedules if s.fecha_especifica is not None]
        assert len(date_specific_schedules) == 2
        specific_dates = {s.fecha_especifica for s in date_specific_schedules}
        assert date1 in specific_dates
        assert date2 in specific_dates
        assert date3 not in specific_dates

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_schedules_by_date_range_weekly_recurring(
        self, async_db_session, async_subject, async_classroom, schedule_repo
    ):
        """Get weekly recurring schedules (no specific date)."""
        s_weekly = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=1,  # Monday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=None,  # Weekly recurring
        )
        s_specific = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=2,  # Tuesday
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            fecha_especifica=date(2024, 1, 16),  # Specific date
        )
        async_db_session.add_all([s_weekly, s_specific])
        await async_db_session.commit()
        
        # Query for any date range
        schedules = await schedule_repo.get_schedules_by_date_range(
            date(2024, 1, 15), date(2024, 1, 20)
        )
        
        # Should get both weekly and date-specific schedules
        weekly_schedules = [s for s in schedules if s.fecha_especifica is None]
        date_specific_schedules = [s for s in schedules if s.fecha_especifica is not None]
        
        assert len(weekly_schedules) == 1
        assert len(date_specific_schedules) == 1
        assert weekly_schedules[0].dia_semana == 1
        assert date_specific_schedules[0].fecha_especifica == date(2024, 1, 16)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_schedules_by_date_range_with_professor_filter(
        self,
        async_db_session,
        async_subject,
        async_subject2,
        async_classroom,
        async_profesor_user,
        schedule_repo,
    ):
        """Get schedules filtered by professor role."""
        s1 = Schedule(
            subject_id=async_subject.id,  # Professor 1's subject
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=date(2024, 1, 15),
        )
        s2 = Schedule(
            subject_id=async_subject2.id,  # Professor 1's other subject (both subjects belong to same professor)
            classroom_id=async_classroom.id,
            dia_semana=2,
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            fecha_especifica=date(2024, 1, 16),
        )
        async_db_session.add_all([s1, s2])
        await async_db_session.commit()
        
        # Query for professor 1's schedules only
        schedules = await schedule_repo.get_schedules_by_date_range(
            date(2024, 1, 14), date(2024, 1, 20),
            user_id=async_profesor_user.id,
            role=UserRole.PROFESOR
        )
        
        # Should get both schedules since both subjects belong to the same professor
        assert len(schedules) == 2
        subject_ids = {s.subject_id for s in schedules}
        assert async_subject.id in subject_ids
        assert async_subject2.id in subject_ids

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_schedules_by_date_range_with_student_filter(
        self,
        async_db_session,
        async_subject,
        async_subject2,
        async_classroom,
        async_estudiante_user,
        async_enrollment,
        schedule_repo,
    ):
        """Get schedules filtered by student role (enrolled subjects only)."""
        s1 = Schedule(
            subject_id=async_subject.id,  # Student is enrolled in this
            classroom_id=async_classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=date(2024, 1, 15),
        )
        s2 = Schedule(
            subject_id=async_subject2.id,  # Student is NOT enrolled in this
            classroom_id=async_classroom.id,
            dia_semana=2,
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
            fecha_especifica=date(2024, 1, 16),
        )
        async_db_session.add_all([s1, s2])
        await async_db_session.commit()
        
        # Query for student's enrolled schedules only
        schedules = await schedule_repo.get_schedules_by_date_range(
            date(2024, 1, 14), date(2024, 1, 20),
            user_id=async_estudiante_user.id,
            role=UserRole.ESTUDIANTE
        )
        
        # Should only get the schedule for the enrolled subject
        assert len(schedules) == 1
        assert schedules[0].subject_id == async_subject.id
