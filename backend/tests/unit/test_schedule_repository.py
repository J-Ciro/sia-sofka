"""Unit tests for ScheduleRepository (Fase 2 - TDD).

TASK-006: Solapamiento de aulas.
TASK-007: Solapamiento de profesor.
TASK-008: Solapamiento de estudiante.
TASK-009: get_weekly_schedule(user_id, role).
"""

import pytest
from datetime import time

from app.models.schedule import Classroom, Schedule
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.repositories.schedule_repository import ScheduleRepository


@pytest.fixture
def schedule_repo(db_session):
    """ScheduleRepository con sesión sync."""
    return ScheduleRepository(db_session)


@pytest.fixture
def classroom2(db_session):
    """Segunda aula para tests de solapamiento."""
    c = Classroom(codigo="AULA-302", nombre="Aula 302", capacidad=30)
    db_session.add(c)
    db_session.commit()
    return c


@pytest.fixture
def subject2(db_session, profesor_user):
    """Segunda materia con el mismo profesor."""
    s = Subject(
        nombre="Física",
        codigo_institucional="FIS301",
        numero_creditos=3,
        profesor_id=profesor_user.id,
    )
    db_session.add(s)
    db_session.commit()
    return s


@pytest.fixture
def enrollment2(db_session, estudiante_user, subject2):
    """Inscripción del estudiante en la segunda materia."""
    e = Enrollment(estudiante_id=estudiante_user.id, subject_id=subject2.id)
    db_session.add(e)
    db_session.commit()
    return e


class TestFindClassroomOverlaps:
    """TASK-006: query de solapamiento de aulas."""

    @pytest.mark.unit
    def test_detect_classroom_overlap_exact(self, db_session, subject, classroom, schedule_repo):
        """Solapamiento exacto: mismo aula, mismo día, mismo rango."""
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        overlaps = schedule_repo.find_classroom_overlaps(
            classroom.id, 1, time(8, 0), time(10, 0)
        )
        assert len(overlaps) == 1
        assert overlaps[0].hora_inicio == time(8, 0)

    @pytest.mark.unit
    def test_detect_classroom_overlap_partial(self, db_session, subject, classroom, schedule_repo):
        """Solapamiento parcial: nuevo 09:00-11:00 vs existente 08:00-10:00."""
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        overlaps = schedule_repo.find_classroom_overlaps(
            classroom.id, 1, time(9, 0), time(11, 0)
        )
        assert len(overlaps) == 1
        assert overlaps[0].hora_inicio == time(8, 0)

    @pytest.mark.unit
    def test_no_classroom_overlap_consecutive(self, db_session, subject, classroom, schedule_repo):
        """Horarios consecutivos 08-10 y 10-12 no solapan."""
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        overlaps = schedule_repo.find_classroom_overlaps(
            classroom.id, 1, time(10, 0), time(12, 0)
        )
        assert len(overlaps) == 0

    @pytest.mark.unit
    def test_exclude_schedule_id_on_update(self, db_session, subject, classroom, schedule_repo):
        """Al editar, excluir el propio horario de la búsqueda de solapamiento."""
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        overlaps = schedule_repo.find_classroom_overlaps(
            classroom.id, 1, time(8, 0), time(10, 0), exclude_schedule_id=s.id
        )
        assert len(overlaps) == 0


class TestFindProfessorOverlaps:
    """TASK-007: query de solapamiento de profesor."""

    @pytest.mark.unit
    def test_detect_professor_overlap(self, db_session, subject, subject2, classroom, classroom2, profesor_user, schedule_repo):
        """Mismo profesor, dos materias, horarios que se solapan."""
        s1 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        s2 = Schedule(
            subject_id=subject2.id,
            classroom_id=classroom2.id,
            dia_semana=1,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        db_session.add_all([s1, s2])
        db_session.commit()
        overlaps = schedule_repo.find_professor_overlaps(
            profesor_user.id, 1, time(9, 0), time(10, 0)
        )
        assert len(overlaps) == 2

    @pytest.mark.unit
    def test_no_professor_overlap_different_days(self, db_session, subject, classroom, profesor_user, schedule_repo):
        """Mismo profesor, distintos días: no conflicto."""
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        overlaps = schedule_repo.find_professor_overlaps(
            profesor_user.id, 2, time(8, 0), time(10, 0)
        )
        assert len(overlaps) == 0


class TestFindStudentOverlaps:
    """TASK-008: query de solapamiento de estudiante."""

    @pytest.mark.unit
    def test_detect_student_overlap(self, db_session, subject, subject2, classroom, classroom2, estudiante_user, enrollment, enrollment2, schedule_repo):
        """Estudiante inscrito en 2 materias con horarios que se solapan."""
        s1 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        s2 = Schedule(
            subject_id=subject2.id,
            classroom_id=classroom2.id,
            dia_semana=1,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        db_session.add_all([s1, s2])
        db_session.commit()
        overlaps = schedule_repo.find_student_overlaps(
            estudiante_user.id, 1, time(9, 0), time(10, 0)
        )
        assert len(overlaps) == 2


class TestGetWeeklySchedule:
    """TASK-009: get_weekly_schedule(user_id, role)."""

    @pytest.mark.unit
    def test_get_professor_weekly_schedule(self, db_session, subject, classroom, profesor_user, schedule_repo):
        """Profesor ve sus horarios (materias que imparte)."""
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        rows = schedule_repo.get_weekly_schedule(profesor_user.id, UserRole.PROFESOR)
        assert len(rows) == 1
        assert rows[0].subject.nombre == "Matemáticas Avanzadas"

    @pytest.mark.unit
    def test_get_student_weekly_schedule(self, db_session, subject, classroom, estudiante_user, enrollment, schedule_repo):
        """Estudiante ve horarios de materias en las que está inscrito."""
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        rows = schedule_repo.get_weekly_schedule(estudiante_user.id, UserRole.ESTUDIANTE)
        assert len(rows) == 1
        assert rows[0].subject.nombre == "Matemáticas Avanzadas"
