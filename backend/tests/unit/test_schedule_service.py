"""Unit tests for ScheduleService (Fase 3 - TDD).

TASK-010: validate_schedule_conflicts
TASK-011: detección de solapamiento
TASK-012: get_professor_schedule
TASK-013: get_student_schedule
"""

import pytest
from datetime import time

from app.models.schedule import Classroom, Schedule
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.services.schedule_service import ScheduleService


@pytest.fixture
def schedule_service(db_session):
    return ScheduleService(db_session)


@pytest.fixture
def classroom2(db_session):
    c = Classroom(codigo="AULA-302", nombre="Aula 302", capacidad=30)
    db_session.add(c)
    db_session.commit()
    return c


@pytest.fixture
def subject2(db_session, profesor_user):
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
    e = Enrollment(estudiante_id=estudiante_user.id, subject_id=subject2.id)
    db_session.add(e)
    db_session.commit()
    return e


class TestValidateScheduleConflicts:
    """TASK-010, TASK-011."""

    @pytest.mark.unit
    def test_validate_schedule_conflicts_sin_conflictos(
        self, db_session, subject, classroom, schedule_service
    ):
        """Sin horarios existentes no hay conflictos."""
        conflicts = schedule_service.validate_schedule_conflicts(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        assert conflicts == []

    @pytest.mark.unit
    def test_validate_schedule_conflicts_conflicto_aula(
        self, db_session, subject, subject2, classroom, schedule_service
    ):
        """Aula ocupada en mismo día y rango solapado."""
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        # Intentar crear 9-11 en la misma aula
        conflicts = schedule_service.validate_schedule_conflicts(
            subject_id=subject2.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        types = [c["type"] for c in conflicts]
        assert "classroom" in types

    @pytest.mark.unit
    def test_validate_schedule_conflicts_conflicto_profesor(
        self, db_session, subject, subject2, classroom, classroom2, profesor_user, schedule_service
    ):
        """Mismo profesor en dos aulas a la misma hora."""
        s1 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s1)
        db_session.commit()
        conflicts = schedule_service.validate_schedule_conflicts(
            subject_id=subject2.id,
            classroom_id=classroom2.id,
            dia_semana=1,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        types = [c["type"] for c in conflicts]
        assert "professor" in types

    @pytest.mark.unit
    def test_validate_schedule_conflicts_exclude_en_edicion(
        self, db_session, subject, classroom, schedule_service
    ):
        """Al editar, excluir el propio horario: no debe dar conflicto consigo mismo."""
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        conflicts = schedule_service.validate_schedule_conflicts(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            exclude_schedule_id=s.id,
        )
        assert conflicts == []


class TestGetProfessorSchedule:
    """TASK-012."""

    @pytest.mark.unit
    def test_get_professor_schedule(
        self, db_session, subject, classroom, profesor_user, schedule_service
    ):
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        rows = schedule_service.get_professor_schedule(profesor_user.id)
        assert len(rows) == 1
        assert rows[0].subject.nombre == "Matemáticas Avanzadas"


class TestGetStudentSchedule:
    """TASK-013."""

    @pytest.mark.unit
    def test_get_student_schedule(
        self, db_session, subject, classroom, estudiante_user, enrollment, schedule_service
    ):
        s = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s)
        db_session.commit()
        rows = schedule_service.get_student_schedule(estudiante_user.id)
        assert len(rows) == 1
        assert rows[0].subject.nombre == "Matemáticas Avanzadas"
