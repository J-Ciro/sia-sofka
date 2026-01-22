"""Unit tests for Schedule and Classroom models.

TDD RED: Tests for Classroom and Schedule models (Fase 1 - feature-horarios-calendario).
Following INVEST: Independent, Negotiable, Valuable, Estimable, Small, Testable.
"""

import pytest
from datetime import time, date
from sqlalchemy.exc import IntegrityError

from app.models.schedule import Classroom, Schedule
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment


class TestClassroomModel:
    """Tests for Classroom (aula) model - TASK-001."""

    @pytest.mark.unit
    def test_create_classroom(self, db_session):
        """Crear aula con capacidad y ubicación."""
        classroom = Classroom(
            codigo="AULA-301",
            nombre="Aula 301",
            capacidad=40,
            ubicacion="Edificio A, Tercer piso",
        )
        db_session.add(classroom)
        db_session.commit()

        assert classroom.id is not None
        assert classroom.codigo == "AULA-301"
        assert classroom.nombre == "Aula 301"
        assert classroom.capacidad == 40
        assert classroom.ubicacion == "Edificio A, Tercer piso"

    @pytest.mark.unit
    def test_classroom_timestamps(self, db_session):
        """Classroom debe tener created_at y updated_at."""
        classroom = Classroom(
            codigo="AULA-302",
            nombre="Aula 302",
            capacidad=30,
        )
        db_session.add(classroom)
        db_session.commit()

        assert classroom.created_at is not None
        assert classroom.updated_at is not None

    @pytest.mark.unit
    def test_classroom_codigo_unique(self, db_session):
        """Código de aula debe ser único."""
        c1 = Classroom(codigo="AULA-101", nombre="Aula 101", capacidad=25)
        db_session.add(c1)
        db_session.commit()

        c2 = Classroom(codigo="AULA-101", nombre="Otra", capacidad=30)
        db_session.add(c2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestScheduleModel:
    """Tests for Schedule model - TASK-002, TASK-003, TASK-004."""

    @pytest.mark.unit
    def test_create_schedule(self, db_session, subject, classroom):
        """Crear horario con asignatura, aula, día, hora_inicio, hora_fin."""
        schedule = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,  # Lunes
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(schedule)
        db_session.commit()

        assert schedule.id is not None
        assert schedule.subject_id == subject.id
        assert schedule.classroom_id == classroom.id
        assert schedule.dia_semana == 1
        assert schedule.hora_inicio == time(8, 0)
        assert schedule.hora_fin == time(10, 0)

    @pytest.mark.unit
    def test_schedule_codigo_generado(self, db_session, subject, classroom):
        """Sistema debe generar código único para el horario (HU-01)."""
        schedule = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(schedule)
        db_session.commit()

        assert schedule.codigo is not None
        assert len(schedule.codigo) > 0

    @pytest.mark.unit
    def test_schedule_timestamps(self, db_session, subject, classroom):
        """Schedule debe tener created_at y updated_at."""
        schedule = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=2,
            hora_inicio=time(9, 0),
            hora_fin=time(11, 0),
        )
        db_session.add(schedule)
        db_session.commit()

        assert schedule.created_at is not None
        assert schedule.updated_at is not None

    @pytest.mark.unit
    def test_schedule_subject_relationship(self, db_session, subject, classroom):
        """Schedule debe tener relación con Subject."""
        schedule = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(schedule)
        db_session.commit()

        assert schedule.subject.id == subject.id
        assert schedule.subject.nombre == "Matemáticas Avanzadas"

    @pytest.mark.unit
    def test_schedule_classroom_relationship(self, db_session, subject, classroom):
        """Schedule debe tener relación con Classroom."""
        schedule = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(schedule)
        db_session.commit()

        assert schedule.classroom.id == classroom.id
        assert schedule.classroom.nombre == "Aula 301"

    @pytest.mark.unit
    def test_schedule_unique_asignatura_dia_hora(self, db_session, subject, classroom):
        """Constraint: (asignatura_id, dia_semana, hora_inicio) debe ser único - TASK-003."""
        s1 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s1)
        db_session.commit()

        # Misma asignatura, mismo día, misma hora_inicio -> debe fallar
        s2 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(9, 0),
        )
        db_session.add(s2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    @pytest.mark.unit
    def test_schedule_misma_asignatura_dia_distinta_hora_ok(self, db_session, subject, classroom):
        """Misma asignatura y día pero distinta hora_inicio debe permitirse."""
        s1 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
        )
        db_session.add(s1)
        db_session.commit()

        s2 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
        )
        db_session.add(s2)
        db_session.commit()

        assert s1.id != s2.id

    @pytest.mark.unit
    def test_schedule_with_fecha_especifica(self, db_session, subject, classroom):
        """Schedule puede tener fecha_especifica para horarios de fecha específica."""
        specific_date = date(2024, 3, 15)  # Friday
        schedule = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=specific_date,
        )
        db_session.add(schedule)
        db_session.commit()

        assert schedule.fecha_especifica == specific_date
        assert schedule.dia_semana == 5

    @pytest.mark.unit
    def test_schedule_fecha_especifica_nullable(self, db_session, subject, classroom):
        """fecha_especifica debe ser nullable para mantener compatibilidad."""
        schedule = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=1,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            # fecha_especifica=None (default)
        )
        db_session.add(schedule)
        db_session.commit()

        assert schedule.fecha_especifica is None
        assert schedule.dia_semana == 1

    @pytest.mark.unit
    def test_schedule_unique_fecha_especifica_constraint(self, db_session, subject, classroom):
        """Constraint: (subject_id, fecha_especifica, hora_inicio) debe ser único."""
        specific_date = date(2024, 3, 15)
        
        s1 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=5,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=specific_date,
        )
        db_session.add(s1)
        db_session.commit()

        # Misma asignatura, misma fecha específica, misma hora_inicio -> debe fallar
        s2 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=5,
            hora_inicio=time(8, 0),
            hora_fin=time(9, 0),
            fecha_especifica=specific_date,
        )
        db_session.add(s2)
        with pytest.raises(IntegrityError):
            db_session.commit()

    @pytest.mark.unit
    def test_schedule_fecha_especifica_different_dates_ok(self, db_session, subject, classroom):
        """Misma asignatura y hora pero fechas específicas diferentes debe permitirse."""
        date1 = date(2024, 3, 15)  # Friday
        date2 = date(2024, 3, 22)  # Next Friday
        
        s1 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=5,
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            fecha_especifica=date1,
        )
        db_session.add(s1)
        db_session.commit()

        s2 = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=5,
            hora_inicio=time(10, 0),  # Different time to avoid weekly constraint conflict
            hora_fin=time(12, 0),
            fecha_especifica=date2,
        )
        db_session.add(s2)
        db_session.commit()

        assert s1.id != s2.id
        assert s1.fecha_especifica != s2.fecha_especifica

    @pytest.mark.unit
    def test_schedule_fecha_especifica_and_weekly_coexist(self, db_session, subject, classroom):
        """Horarios con fecha específica y semanales pueden coexistir."""
        specific_date = date(2024, 3, 15)  # Friday
        
        # Horario semanal (sin fecha específica)
        weekly_schedule = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(8, 0),
            hora_fin=time(10, 0),
            # fecha_especifica=None
        )
        db_session.add(weekly_schedule)
        db_session.commit()

        # Horario para fecha específica (mismo día de semana)
        specific_schedule = Schedule(
            subject_id=subject.id,
            classroom_id=classroom.id,
            dia_semana=5,  # Friday
            hora_inicio=time(10, 0),  # Different time
            hora_fin=time(12, 0),
            fecha_especifica=specific_date,
        )
        db_session.add(specific_schedule)
        db_session.commit()

        assert weekly_schedule.fecha_especifica is None
        assert specific_schedule.fecha_especifica == specific_date
        assert weekly_schedule.id != specific_schedule.id
