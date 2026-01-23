"""Subject service with business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.repositories.subject_repository import SubjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.models.subject import Subject
from app.models.user import UserRole
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.models.attendance import ClaseSession, Attendance
from app.core.exceptions import ConflictError


class SubjectService:
    """Service for subject business logic."""
    
    def __init__(self, db: AsyncSession):
        """Initialize subject service.
        
        Args:
            db: Database session
        """
        self.repository = SubjectRepository(db)
        self.user_repository = UserRepository(db)
        self.db = db
    
    def _validate_credits(self, credits: int) -> None:
        """Validate number of credits.
        
        Args:
            credits: Number of credits to validate
        
        Raises:
            ValueError: If credits are invalid
        """
        if credits <= 0 or credits > 10:
            raise ValueError("Number of credits must be between 1 and 10")
    
    async def _validate_profesor(self, profesor_id: int) -> None:
        """Validate that profesor exists and is a Profesor.
        
        Args:
            profesor_id: Profesor user ID
        
        Raises:
            ValueError: If profesor not found or invalid
        """
        profesor = await self.user_repository.get_by_id(profesor_id)
        if not profesor:
            raise ValueError("Profesor not found")
        if profesor.role != UserRole.PROFESOR:
            raise ValueError("User is not a Profesor")
    
    async def create_subject(self, subject_data: SubjectCreate) -> Subject:
        """Create a new subject with business logic.
        
        Args:
            subject_data: Subject creation data
        
        Returns:
            Created subject
        
        Raises:
            ValueError: If invalid data or profesor not found
        """
        # Validate credits
        self._validate_credits(subject_data.numero_creditos)
        
        # Validate profesor
        await self._validate_profesor(subject_data.profesor_id)
        
        # Generate codigo_institucional if not provided
        from app.utils.codigo_generator import generar_codigo_materia
        codigo_institucional = subject_data.codigo_institucional
        if not codigo_institucional:
            codigo_institucional = await generar_codigo_materia(self.db, subject_data.nombre)
        else:
            # Check if provided codigo_institucional already exists
            existing = await self.repository.get_by_codigo_institucional(codigo_institucional)
            if existing:
                raise ValueError("Subject code already exists")
        
        # Create subject
        subject_dict = subject_data.model_dump(exclude={'codigo_institucional'})
        subject_dict['codigo_institucional'] = codigo_institucional
        return await self.repository.create(subject_dict)
    
    async def get_subject_by_id(self, subject_id: int) -> Subject | None:
        """Get subject by ID.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            Subject or None
        """
        return await self.repository.get_by_id(subject_id)
    
    async def update_subject(
        self, subject_id: int, subject_data: SubjectUpdate
    ) -> Subject | None:
        """Update subject with business logic.
        
        Args:
            subject_id: Subject ID
            subject_data: Subject update data
        
        Returns:
            Updated subject or None
        
        Raises:
            ValueError: If invalid data
        """
        # Validate credits if provided
        if subject_data.numero_creditos is not None:
            self._validate_credits(subject_data.numero_creditos)
        
        # Validate profesor if provided
        if subject_data.profesor_id is not None:
            await self._validate_profesor(subject_data.profesor_id)
        
        update_dict = subject_data.model_dump(exclude_unset=True)
        return await self.repository.update(subject_id, update_dict)
    
    async def delete_subject(self, subject_id: int) -> bool:
        """Delete subject with validation of historical data.
        
        Strategy:
        - OPERATIONAL data (auto-deleted): Enrollments, Schedules, Stats, Alerts
        - HISTORICAL data (blocked): Grades, Attendances
        
        Blocks deletion if subject has:
        - Grades (historical academic records)
        - Attendances (historical attendance records)
        
        Args:
            subject_id: Subject ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            ConflictError: If subject has historical data that prevents deletion
        """
        # Get subject
        subject = await self.repository.get_by_id(subject_id)
        if not subject:
            return False
        
        # Check for HISTORICAL data that must be preserved
        historical_conflicts = []
        
        # Check if subject has enrollments with grades
        enrollments_stmt = select(Enrollment).where(Enrollment.subject_id == subject_id)
        enrollments_result = await self.db.execute(enrollments_stmt)
        enrollments = enrollments_result.scalars().all()
        
        if enrollments:
            # Check if any enrollment has grades
            enrollment_ids = [e.id for e in enrollments]
            grades_stmt = select(Grade).where(Grade.enrollment_id.in_(enrollment_ids))
            grades_result = await self.db.execute(grades_stmt)
            grades = grades_result.scalars().all()
            
            if grades:
                historical_conflicts.append(
                    f"La materia tiene {len(grades)} calificación(es) históricas en "
                    f"{len(enrollments)} inscripción(es). "
                    f"Las calificaciones son parte del historial académico y no pueden eliminarse."
                )
        
        # Check if subject has sessions with attendance records
        sessions_stmt = select(ClaseSession).where(ClaseSession.subject_id == subject_id)
        sessions_result = await self.db.execute(sessions_stmt)
        sessions = sessions_result.scalars().all()
        
        if sessions:
            # Check if any session has attendance records
            session_ids = [s.id for s in sessions]
            attendance_stmt = select(Attendance).where(
                Attendance.clase_session_id.in_(session_ids)
            )
            attendance_result = await self.db.execute(attendance_stmt)
            attendances = attendance_result.scalars().all()
            
            if attendances:
                historical_conflicts.append(
                    f"La materia tiene {len(sessions)} sesión(es) con "
                    f"{len(attendances)} registro(s) de asistencia históricos. "
                    f"Los registros de asistencia son parte del historial académico y no pueden eliminarse."
                )
        
        # If there are historical conflicts, block deletion
        if historical_conflicts:
            error_message = (
                "No se puede eliminar la materia porque tiene datos históricos que deben preservarse:\n"
                + "\n".join(f"- {c}" for c in historical_conflicts)
            )
            raise ConflictError(error_message)
        
        # No historical conflicts - proceed with deletion
        # SQLAlchemy cascade will handle: enrollments, sessions, schedules, stats, alerts
        return await self.repository.delete(subject_id)
    
    async def get_subjects_by_profesor(
        self, profesor_id: int, skip: int = 0, limit: int = 100
    ) -> list[Subject]:
        """Get subjects by profesor.
        
        Args:
            profesor_id: Profesor user ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of subjects
        """
        return await self.repository.get_by_profesor(profesor_id, skip, limit)


