"""Unit tests for Attendance Repository (Async).

Tests for AttendanceRepository CRUD operations following TDD methodology.
Updated to use async methods after refactoring to inherit from AbstractRepository."""

import pytest
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.attendance import (
    ClaseSession,
    Attendance,
    AttendanceStatus,
    AttendanceStats,
)
from app.repositories.attendance_repository import AttendanceRepository
from app.core.exceptions import NotFoundError


class TestAttendanceRepository:
    """Tests for AttendanceRepository (async)."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_create_attendance(self, async_db_session, async_clase_session, async_estudiante_user):
        """Test creating an attendance record using AbstractRepository.create()."""
        repo = AttendanceRepository(async_db_session)
        
        attendance = await repo.create({
            "clase_session_id": async_clase_session.id,
            "estudiante_id": async_estudiante_user.id,
            "estado": AttendanceStatus.PRESENTE,
        })
        
        assert attendance.id is not None
        assert attendance.estado == AttendanceStatus.PRESENTE

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_attendance_by_id(self, async_db_session, async_clase_session, async_estudiante_user):
        """Test retrieving an attendance record by ID using AbstractRepository.get_by_id()."""
        repo = AttendanceRepository(async_db_session)
        
        # Create attendance
        created = await repo.create({
            "clase_session_id": async_clase_session.id,
            "estudiante_id": async_estudiante_user.id,
            "estado": AttendanceStatus.PRESENTE,
        })
        
        # Retrieve it using AbstractRepository method
        retrieved = await repo.get_by_id(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.estado == AttendanceStatus.PRESENTE

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_update_attendance_status(self, async_db_session, async_clase_session, async_estudiante_user):
        """Test updating attendance status using AbstractRepository.update()."""
        repo = AttendanceRepository(async_db_session)
        
        # Create with PRESENTE
        attendance = await repo.create({
            "clase_session_id": async_clase_session.id,
            "estudiante_id": async_estudiante_user.id,
            "estado": AttendanceStatus.PRESENTE,
        })
        
        # Update to AUSENTE using AbstractRepository method
        updated = await repo.update(
            attendance.id,
            {"estado": AttendanceStatus.AUSENTE}
        )
        
        assert updated is not None
        assert updated.estado == AttendanceStatus.AUSENTE

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_attendance_by_session_and_student(self, async_db_session, async_clase_session, async_estudiante_user):
        """Test retrieving attendance by session and student (async)."""
        repo = AttendanceRepository(async_db_session)
        
        created = await repo.create({
            "clase_session_id": async_clase_session.id,
            "estudiante_id": async_estudiante_user.id,
            "estado": AttendanceStatus.PRESENTE,
        })
        
        retrieved = await repo.get_by_session_and_student(
            async_clase_session.id,
            async_estudiante_user.id,
        )
        
        assert retrieved is not None
        assert retrieved.id == created.id

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_attendance_by_session_and_student_not_found(self, async_db_session, async_clase_session, async_estudiante_user):
        """Test retrieving non-existent attendance returns None."""
        repo = AttendanceRepository(async_db_session)
        
        retrieved = await repo.get_by_session_and_student(
            async_clase_session.id,
            999,  # Non-existent student
        )
        
        assert retrieved is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_all_attendance_by_session(self, async_db_session, async_clase_session, async_profesor_user):
        """Test retrieving all attendance records for a session (async with pagination)."""
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        
        repo = AttendanceRepository(async_db_session)
        
        # Create 3 students
        students = []
        for i in range(3):
            student = User(
                email=f"student{i}@test.com",
                password_hash=hashpw(b"password123", gensalt()).decode(),
                role=UserRole.ESTUDIANTE,
                nombre=f"Student{i}",
                apellido="Test",
                codigo_institucional=f"EST10{i}",
                fecha_nacimiento=date(2005, 3, 20),
            )
            async_db_session.add(student)
            await async_db_session.commit()
            await async_db_session.refresh(student)
            students.append(student)
        
        # Create attendance for all 3 students
        for student in students:
            await repo.create({
                "clase_session_id": async_clase_session.id,
                "estudiante_id": student.id,
                "estado": AttendanceStatus.PRESENTE,
            })
        
        # Retrieve all attendance for this session (async with pagination)
        attendances = await repo.get_all_by_session(async_clase_session.id)
        
        assert len(attendances) == 3
        assert all(a.clase_session_id == async_clase_session.id for a in attendances)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_get_attendance_by_student_and_subject(self, async_db_session, async_subject, async_estudiante_user, async_profesor_user):
        """Test retrieving attendance for a student in a specific subject (async)."""
        from app.models.enrollment import Enrollment
        
        repo = AttendanceRepository(async_db_session)
        
        # Create enrollment
        enrollment = Enrollment(
            estudiante_id=async_estudiante_user.id,
            subject_id=async_subject.id,
        )
        async_db_session.add(enrollment)
        await async_db_session.commit()
        
        # Create multiple sessions for the subject
        today = date.today()
        clase1 = ClaseSession(
            subject_id=async_subject.id,
            fecha=today,
            hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
            hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
            creado_por=async_profesor_user.id,
        )
        async_db_session.add(clase1)
        await async_db_session.commit()
        await async_db_session.refresh(clase1)
        
        tomorrow = date(today.year, today.month, today.day + 1)
        clase2 = ClaseSession(
            subject_id=async_subject.id,
            fecha=tomorrow,
            hora_inicio=datetime.combine(tomorrow, datetime.min.time().replace(hour=8)),
            hora_fin=datetime.combine(tomorrow, datetime.min.time().replace(hour=10)),
            creado_por=async_profesor_user.id,
        )
        async_db_session.add(clase2)
        await async_db_session.commit()
        await async_db_session.refresh(clase2)
        
        # Create attendance records
        await repo.create({
            "clase_session_id": clase1.id,
            "estudiante_id": async_estudiante_user.id,
            "estado": AttendanceStatus.PRESENTE,
        })
        await repo.create({
            "clase_session_id": clase2.id,
            "estudiante_id": async_estudiante_user.id,
            "estado": AttendanceStatus.AUSENTE,
        })
        
        # Retrieve by student and subject (async)
        attendances = await repo.get_by_student_and_subject(
            async_estudiante_user.id,
            async_subject.id,
        )
        
        assert len(attendances) == 2

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_calculate_attendance_percentage_async(self, async_db_session, async_clase_session, async_profesor_user):
        """Test calculating attendance percentage (async)."""
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        
        repo = AttendanceRepository(async_db_session)
        
        # Create 10 students with different statuses
        # 6 PRESENTE, 2 AUSENTE, 2 TARDANZA
        students = []
        statuses = (
            [AttendanceStatus.PRESENTE] * 6 +
            [AttendanceStatus.AUSENTE] * 2 +
            [AttendanceStatus.TARDANZA] * 2
        )
        
        for i, status in enumerate(statuses):
            student = User(
                email=f"student{i+100}@test.com",
                password_hash=hashpw(b"password123", gensalt()).decode(),
                role=UserRole.ESTUDIANTE,
                nombre=f"Student{i+100}",
                apellido="Test",
                codigo_institucional=f"EST20{i}",
                fecha_nacimiento=date(2005, 3, 20),
            )
            async_db_session.add(student)
            await async_db_session.commit()
            await async_db_session.refresh(student)
            students.append(student)
            
            await repo.create({
                "clase_session_id": async_clase_session.id,
                "estudiante_id": student.id,
                "estado": status,
            })
        
        # Calculate percentage (PRESENTE + TARDANZA) / TOTAL (async)
        # (6 + 2) / 10 = 80%
        percentage = await repo.calculate_attendance_percentage_async(
            async_clase_session.id,
        )
        
        assert percentage == 80.0

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_count_by_status_async(self, async_db_session, async_clase_session, async_profesor_user):
        """Test counting attendance records by status (async)."""
        from app.models.user import User, UserRole
        from bcrypt import hashpw, gensalt
        
        repo = AttendanceRepository(async_db_session)
        
        # Create students with different statuses
        statuses = [
            AttendanceStatus.PRESENTE,
            AttendanceStatus.PRESENTE,
            AttendanceStatus.AUSENTE,
            AttendanceStatus.TARDANZA,
        ]
        
        for i, status in enumerate(statuses):
            student = User(
                email=f"student{i+200}@test.com",
                password_hash=hashpw(b"password123", gensalt()).decode(),
                role=UserRole.ESTUDIANTE,
                nombre=f"Student{i+200}",
                apellido="Test",
                codigo_institucional=f"EST30{i}",
                fecha_nacimiento=date(2005, 3, 20),
            )
            async_db_session.add(student)
            await async_db_session.commit()
            await async_db_session.refresh(student)
            
            await repo.create({
                "clase_session_id": async_clase_session.id,
                "estudiante_id": student.id,
                "estado": status,
            })
        
        # Count by status (async)
        counts = await repo.count_by_status_async(async_clase_session.id)
        
        assert counts[AttendanceStatus.PRESENTE] == 2
        assert counts[AttendanceStatus.AUSENTE] == 1
        assert counts[AttendanceStatus.TARDANZA] == 1

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_delete_attendance(self, async_db_session, async_clase_session, async_estudiante_user):
        """Test deleting an attendance record using AbstractRepository.delete()."""
        repo = AttendanceRepository(async_db_session)
        
        created = await repo.create({
            "clase_session_id": async_clase_session.id,
            "estudiante_id": async_estudiante_user.id,
            "estado": AttendanceStatus.PRESENTE,
        })
        
        # Delete using AbstractRepository method
        deleted = await repo.delete(created.id)
        assert deleted is True
        
        # Verify it's gone
        retrieved = await repo.get_by_id(created.id)
        assert retrieved is None
