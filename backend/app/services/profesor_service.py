"""Profesor service with profesor-specific business logic."""

from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.subject import Subject
from app.models.grade import Grade
from app.services.subject_service import SubjectService
from app.services.grade_service import GradeService
from app.services.user_service import UserService
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.subject_repository import SubjectRepository
from app.schemas.grade import GradeCreate
from app.schemas.user import UserUpdate


class ProfesorService:
    """Service for profesor-specific business logic."""
    
    def __init__(self, db: AsyncSession, profesor_user: User):
        """Initialize profesor service.
        
        Args:
            db: Database session
            profesor_user: Profesor user instance
        """
        self.db = db
        self.profesor_user = profesor_user
        self.subject_service = SubjectService(db)
        self.grade_service = GradeService(db)
        self.user_service = UserService(db)
        self.enrollment_repo = EnrollmentRepository(db)
        self.subject_repo = SubjectRepository(db)
    
    async def get_assigned_subjects(self) -> list[Subject]:
        """Get all subjects assigned to this profesor.
        
        Returns:
            List of assigned subjects
        """
        return await self.subject_repo.get_by_profesor(int(self.profesor_user.id))
    
    async def get_students_by_subject(self, subject_id: int) -> list[User]:
        """Get all students enrolled in a subject assigned to this profesor.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            List of estudiantes
        
        Raises:
            ValueError: If subject is not assigned to this profesor
        """
        # Verify subject is assigned to this profesor
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject or subject.profesor_id != self.profesor_user.id:
            raise ValueError("Subject is not assigned to this profesor")
        
        # Get enrollments with eager-loaded estudiante relationships (batch query)
        enrollments = await self.enrollment_repo.get_many_with_relations(
            subject_id=subject_id,
            relations=['estudiante']
        )
        
        # Extract estudiantes from enrollments (already loaded)
        estudiantes = []
        for enrollment in enrollments:
            if hasattr(enrollment, 'estudiante') and enrollment.estudiante:
                estudiantes.append(enrollment.estudiante)
        
        return estudiantes
    
    async def create_grade(
        self, grade_data: GradeCreate, subject_id: int
    ) -> Grade:
        """Create a grade for a student in an assigned subject.
        
        Args:
            grade_data: Grade creation data
            subject_id: Subject ID (must be assigned to this profesor)
        
        Returns:
            Created grade
        
        Raises:
            ValueError: If subject is not assigned to this profesor or enrollment invalid
        """
        # Verify subject is assigned to this profesor
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject or subject.profesor_id != self.profesor_user.id:
            raise ValueError("Subject is not assigned to this profesor")
        
        # Verify enrollment exists and is for this subject
        enrollment = await self.enrollment_repo.get_by_id(grade_data.enrollment_id)
        if not enrollment or enrollment.subject_id != subject_id:
            raise ValueError("Invalid enrollment for this subject")
        
        # Create grade
        return await self.grade_service.create_grade(grade_data)
    
    async def get_subject_with_students(self, subject_id: int) -> dict:
        """Get subject with list of enrolled students.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            Dictionary with subject and students
        
        Raises:
            ValueError: If subject is not assigned to this profesor
        """
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject or subject.profesor_id != self.profesor_user.id:
            raise ValueError("Subject is not assigned to this profesor")
        
        students = await self.get_students_by_subject(subject_id)
        
        return {
            "subject": subject,
            "students": students,
        }
    
    async def _build_subject_report_data(self, subject, enrollments) -> dict:
        """Build report data structure for a subject.
        
        Args:
            subject: Subject instance
            enrollments: List of enrollments with loaded estudiantes
        
        Returns:
            Dictionary with report data structure
        """
        report_data: dict[str, Any] = {
            "subject": {
                "id": subject.id,
                "nombre": subject.nombre,
                "codigo_institucional": subject.codigo_institucional,
            },
            "students": [],
        }
        
        for enrollment in enrollments:
            # Estudiante already loaded via eager loading
            estudiante = getattr(enrollment, 'estudiante', None)
            if not estudiante:
                continue
            
            grades = await self.grade_service.get_grades_by_enrollment(enrollment.id)
            try:
                average = await self.grade_service.calculate_average(enrollment.id)
            except ValueError:
                average = None
            
            report_data["students"].append({
                "estudiante": {
                    "id": estudiante.id,
                    "nombre": estudiante.nombre,
                    "apellido": estudiante.apellido,
                    "codigo_institucional": estudiante.codigo_institucional,
                },
                "grades": [{"nota": float(g.nota), "periodo": g.periodo, "fecha": str(g.fecha)} for g in grades],
                "average": float(average) if average else None,
            })
        
        return report_data
    
    async def generate_subject_report(
        self, subject_id: int, format: str = "pdf"
    ) -> dict:
        """Generate report of grades for a subject using Factory Method.
        
        Args:
            subject_id: Subject ID
            format: Report format (pdf, html, json)
        
        Returns:
            Report with content, filename, and content_type
        """
        from app.factories import ReportFactory  # Import from __init__.py to ensure generators are registered
        
        # Verify subject is assigned
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject or subject.profesor_id != self.profesor_user.id:
            raise ValueError("Subject is not assigned to this profesor")
        
        # Get enrollments with eager-loaded estudiante relationships (batch query)
        enrollments = await self.enrollment_repo.get_many_with_relations(
            subject_id=subject_id,
            relations=['estudiante']
        )
        
        # Build report data
        report_data = await self._build_subject_report_data(subject, enrollments)
        
        # Use Factory Method to generate report
        generator = ReportFactory.create_generator(format)
        return generator.generate(report_data)
    
    async def update_profile(self, user_data: UserUpdate) -> User:
        """Update profesor's own profile.
        
        Args:
            user_data: User update data
        
        Returns:
            Updated profesor
        
        Raises:
            NotFoundError: If user not found
        """
        updated = await self.user_service.update_user(int(self.profesor_user.id), user_data)
        if not updated:
            raise NotFoundError("User", int(self.profesor_user.id))
        return updated

