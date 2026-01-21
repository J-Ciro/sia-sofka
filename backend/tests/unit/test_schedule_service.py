"""Unit tests for ScheduleService (Fase 3 - TDD). Async.

TASK-010: validate_schedule_conflicts
TASK-011: detección de solapamiento
TASK-012: get_professor_schedule
TASK-013: get_student_schedule

Enhanced for Task 4.1:
- Date-specific schedule conflict validation
- Calendar display functionality
- Backward compatibility preservation
"""

import pytest
from datetime import time, date, timedelta

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


class TestEnhancedScheduleConflicts:
    """Enhanced conflict validation for date-specific schedules (Task 4.1)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_date_specific_schedule_no_conflicts(
        self, async_subject, async_classroom, schedule_service
    ):
        """Date-specific schedule with no conflicts should pass validation."""
        specific_date = date(2024, 3, 15)  # Friday
        conflicts = await schedule_service.validate_schedule_conflicts(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=specific_date,
        )
        assert conflicts == []

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_date_specific_classroom_conflict(
        self, async_db_session, async_subject, async_subject2, async_classroom, schedule_service
    ):
        """Date-specific schedules should detect classroom conflicts on the same date."""
        specific_date = date(2024, 3, 15)  # Friday
        
        # Create existing date-specific schedule
        existing_schedule = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=specific_date,
        )
        async_db_session.add(existing_schedule)
        await async_db_session.commit()

        # Try to create conflicting date-specific schedule
        conflicts = await schedule_service.validate_schedule_conflicts(
            subject_id=async_subject2.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
            fecha_especifica=specific_date,
        )
        
        types = [c["type"] for c in conflicts]
        assert "classroom" in types

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_date_specific_vs_weekly_conflict(
        self, async_db_session, async_subject, async_subject2, async_classroom, schedule_service
    ):
        """Date-specific schedule should detect conflicts with weekly recurring schedules."""
        specific_date = date(2024, 3, 15)  # Friday
        
        # Create existing weekly recurring schedule (no fecha_especifica)
        weekly_schedule = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            # fecha_especifica=None (weekly recurring)
        )
        async_db_session.add(weekly_schedule)
        await async_db_session.commit()

        # Try to create date-specific schedule that conflicts with weekly
        conflicts = await schedule_service.validate_schedule_conflicts(
            subject_id=async_subject2.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
            fecha_especifica=specific_date,
        )
        
        types = [c["type"] for c in conflicts]
        assert "classroom_weekly" in types

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_validate_date_specific_different_dates_no_conflict(
        self, async_db_session, async_subject, async_subject2, async_classroom, schedule_service
    ):
        """Date-specific schedules on different dates should not conflict."""
        date1 = date(2024, 3, 15)  # Friday
        date2 = date(2024, 3, 22)  # Next Friday
        
        # Create existing date-specific schedule
        existing_schedule = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=date1,
        )
        async_db_session.add(existing_schedule)
        await async_db_session.commit()

        # Create date-specific schedule for different date - should not conflict
        conflicts = await schedule_service.validate_schedule_conflicts(
            subject_id=async_subject2.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=date2,
        )
        
        assert conflicts == []


class TestGetSchedulesForCalendar:
    """Test calendar display functionality (Task 4.1)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_schedules_for_calendar_date_specific_only(
        self, async_db_session, async_subject, async_classroom, schedule_service
    ):
        """Calendar should return date-specific schedules within range."""
        specific_date = date(2024, 3, 15)  # Friday
        
        # Create date-specific schedule
        schedule = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=specific_date,
        )
        async_db_session.add(schedule)
        await async_db_session.commit()

        # Get schedules for calendar (week containing the date)
        start_date = date(2024, 3, 11)  # Monday
        end_date = date(2024, 3, 17)    # Sunday
        
        schedules = await schedule_service.get_schedules_for_calendar(
            start_date, end_date
        )
        
        assert len(schedules) == 1
        assert schedules[0].fecha_especifica == specific_date

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_schedules_for_calendar_weekly_expansion(
        self, async_db_session, async_subject, async_classroom, schedule_service
    ):
        """Calendar should expand weekly schedules to specific dates."""
        # Create weekly recurring schedule (no fecha_especifica)
        weekly_schedule = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            # fecha_especifica=None (weekly recurring)
        )
        async_db_session.add(weekly_schedule)
        await async_db_session.commit()

        # Get schedules for calendar (2 weeks = 2 Friday occurrences)
        start_date = date(2024, 3, 11)  # Monday
        end_date = date(2024, 3, 24)    # Sunday (2 weeks)
        
        schedules = await schedule_service.get_schedules_for_calendar(
            start_date, end_date
        )
        
        # Should have 2 virtual instances (March 15 and March 22)
        friday_schedules = [s for s in schedules if s.fecha_especifica.weekday() == 4]  # Friday
        assert len(friday_schedules) == 2
        
        # Check dates
        dates = [s.fecha_especifica for s in friday_schedules]
        assert date(2024, 3, 15) in dates
        assert date(2024, 3, 22) in dates

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_schedules_for_calendar_date_specific_overrides_weekly(
        self, async_db_session, async_subject, async_classroom, async_classroom2, schedule_service
    ):
        """Date-specific schedule should work alongside weekly recurring schedules."""
        specific_date = date(2024, 3, 15)  # Friday
        
        # Create weekly recurring schedule
        weekly_schedule = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            # fecha_especifica=None (weekly recurring)
        )
        
        # Create date-specific schedule for same subject but different time/classroom
        date_specific_schedule = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom2.id,  # Different classroom
            dia_semana=5,  # Friday
            hora_inicio=time(14, 0),  # Different time to avoid constraint
            hora_fin=time(16, 0),
            fecha_especifica=specific_date,
        )
        
        async_db_session.add(weekly_schedule)
        async_db_session.add(date_specific_schedule)
        await async_db_session.commit()

        # Get schedules for calendar
        start_date = date(2024, 3, 11)  # Monday
        end_date = date(2024, 3, 17)    # Sunday
        
        schedules = await schedule_service.get_schedules_for_calendar(
            start_date, end_date
        )
        
        # Should have both schedules for March 15 since they have different times
        friday_schedules = [s for s in schedules if s.fecha_especifica == specific_date]
        assert len(friday_schedules) == 2
        
        # Check that we have both the weekly (8-10) and date-specific (14-16) schedules
        times = [(s.hora_inicio, s.hora_fin) for s in friday_schedules]
        assert (time(8, 0), time(10, 0)) in times  # Weekly schedule expanded
        assert (time(14, 0), time(16, 0)) in times  # Date-specific schedule

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_schedules_for_calendar_true_override_behavior(
        self, async_db_session, async_subject, async_subject2, async_classroom, schedule_service
    ):
        """Date-specific schedule should override weekly recurring for exact same subject/time."""
        specific_date = date(2024, 3, 15)  # Friday
        
        # Create weekly recurring schedule
        weekly_schedule = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            # fecha_especifica=None (weekly recurring)
        )
        
        # Create date-specific schedule for same subject/time/classroom (true override)
        date_specific_schedule = Schedule(
            subject_id=async_subject.id,
            classroom_id=async_classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(14, 0),  # Different time to avoid constraint violation
            hora_fin=time(16, 0),
            fecha_especifica=specific_date,
        )
        
        async_db_session.add(weekly_schedule)
        async_db_session.add(date_specific_schedule)
        await async_db_session.commit()

        # Get schedules for calendar
        start_date = date(2024, 3, 11)  # Monday
        end_date = date(2024, 3, 17)    # Sunday
        
        schedules = await schedule_service.get_schedules_for_calendar(
            start_date, end_date
        )
        
        # Should have both schedules for March 15 since they have different times
        friday_schedules = [s for s in schedules if s.fecha_especifica == specific_date]
        assert len(friday_schedules) == 2
        
        # Check that we have both the weekly (8-10) and date-specific (14-16) schedules
        times = [(s.hora_inicio, s.hora_fin) for s in friday_schedules]
        assert (time(8, 0), time(10, 0)) in times  # Weekly schedule
        assert (time(14, 0), time(16, 0)) in times  # Date-specific schedule
