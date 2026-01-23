"""Admin service with admin-specific business logic."""

from decimal import Decimal
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.services.user_service import UserService
from app.services.subject_service import SubjectService
from app.services.grade_service import GradeService
from app.repositories.enrollment_repository import EnrollmentRepository
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.subject import SubjectCreate, SubjectUpdate


class AdminService:
    """Service for admin-specific business logic."""
    
    def __init__(self, db: AsyncSession, admin_user: User):
        """Initialize admin service.
        
        Args:
            db: Database session
            admin_user: Admin user instance
        """
        self.db = db
        self.admin_user = admin_user
        self.user_service = UserService(db)
        self.subject_service = SubjectService(db)
        self.grade_service = GradeService(db)
        self.enrollment_repo = EnrollmentRepository(db)
    
    # User Management
    
    async def create_estudiante(self, user_data: UserCreate) -> User:
        """Create a new estudiante.
        
        Args:
            user_data: Estudiante creation data
        
        Returns:
            Created estudiante
        
        Raises:
            ValueError: If role is not Estudiante
        """
        if user_data.role != UserRole.ESTUDIANTE:
            raise ValueError("Role must be Estudiante")
        return await self.user_service.create_user(user_data)
    
    async def create_profesor(self, user_data: UserCreate) -> User:
        """Create a new profesor.
        
        Args:
            user_data: Profesor creation data
        
        Returns:
            Created profesor
        
        Raises:
            ValueError: If role is not Profesor
        """
        if user_data.role != UserRole.PROFESOR:
            raise ValueError("Role must be Profesor")
        return await self.user_service.create_user(user_data)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User | None:
        """Update a user.
        
        Args:
            user_id: User ID
            user_data: User update data
        
        Returns:
            Updated user or None
        """
        return await self.user_service.update_user(user_id, user_data)
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete a user.
        
        Args:
            user_id: User ID
        
        Returns:
            True if deleted, False if not found
        """
        return await self.user_service.delete_user(user_id)
    
    async def get_all_estudiantes(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all estudiantes.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of estudiantes
        """
        return await self.user_service.get_users_by_role(
            UserRole.ESTUDIANTE.value, skip, limit
        )
    
    async def get_all_profesores(self, skip: int = 0, limit: int = 100) -> list[User]:
        """Get all profesores.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of profesores
        """
        return await self.user_service.get_users_by_role(
            UserRole.PROFESOR.value, skip, limit
        )
    
    # Subject Management
    
    async def create_subject(self, subject_data: SubjectCreate) -> Subject:
        """Create a new subject.
        
        Args:
            subject_data: Subject creation data
        
        Returns:
            Created subject
        """
        return await self.subject_service.create_subject(subject_data)
    
    async def update_subject(
        self, subject_id: int, subject_data: SubjectUpdate
    ) -> Subject | None:
        """Update a subject.
        
        Args:
            subject_id: Subject ID
            subject_data: Subject update data
        
        Returns:
            Updated subject or None
        """
        return await self.subject_service.update_subject(subject_id, subject_data)
    
    async def delete_subject(self, subject_id: int) -> bool:
        """Delete a subject.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            True if deleted, False if not found
        """
        return await self.subject_service.delete_subject(subject_id)
    
    # Average Calculation
    
    async def generate_average(
        self, estudiante_id: int, subject_id: int
    ) -> Decimal:
        """Generate average grade for estudiante in a subject.
        
        Args:
            estudiante_id: Estudiante user ID
            subject_id: Subject ID
        
        Returns:
            Average grade as Decimal
        
        Raises:
            ValueError: If enrollment not found or no grades
        """
        # Find enrollment
        enrollment = await self.enrollment_repo.get_by_estudiante_and_subject(
            estudiante_id, subject_id
        )
        
        if not enrollment:
            raise ValueError("Estudiante is not enrolled in this subject")
        
        # Calculate average
        return await self.grade_service.calculate_average(enrollment.id)
    
    # Report Generation using Factory Method
    async def _build_student_report_data(self, estudiante, enrollments) -> dict:
        """Build report data structure for a student.
        
        Args:
            estudiante: Estudiante user instance
            enrollments: List of enrollments with loaded subjects
        
        Returns:
            Dictionary with report data structure
        """
        report_data = {
            "estudiante": {
                "id": estudiante.id,
                "nombre": estudiante.nombre,
                "apellido": estudiante.apellido,
                "codigo_institucional": estudiante.codigo_institucional,
                "programa_academico": estudiante.programa_academico,
            },
            "subjects": [],
        }  # type: dict[str, Any]
        
        # Add enrollment and grade data (subjects already loaded via eager loading)
        for enrollment in enrollments:
            # Subject already loaded via eager loading
            subject = getattr(enrollment, 'subject', None)
            if not subject:
                continue
            
            grades = await self.grade_service.get_grades_by_enrollment(enrollment.id)
            try:
                average = await self.grade_service.calculate_average(enrollment.id)
            except ValueError:
                average = None
            
            report_data["subjects"].append({
                "subject": {
                    "id": subject.id,
                    "nombre": subject.nombre,
                    "codigo_institucional": subject.codigo_institucional,
                    "numero_creditos": subject.numero_creditos,
                },
                "grades": [{"nota": float(g.nota), "periodo": g.periodo, "fecha": str(g.fecha)} for g in grades],
                "average": float(average) if average else None,
            })
        
        return report_data
    
    def _calculate_general_average(self, report_data: dict) -> None:
        """Calculate and add general weighted average to report data.
        
        Args:
            report_data: Report data dictionary (modified in place)
        """
        total_weighted_sum = Decimal("0.0")
        total_credits = Decimal("0.0")
        for subject_info in report_data["subjects"]:
            if subject_info["average"] is not None:
                credits = Decimal(str(subject_info["subject"]["numero_creditos"]))
                average = Decimal(str(subject_info["average"]))
                total_weighted_sum += average * credits
                total_credits += credits
        
        if total_credits > 0:
            general_average = float(total_weighted_sum / total_credits)
            report_data["general_average"] = round(general_average, 2)
        else:
            report_data["general_average"] = None
    
    async def generate_student_report(
        self, estudiante_id: int, format: str = "json"
    ) -> dict:
        """Generate report for a student using Factory Method.
        
        Args:
            estudiante_id: Estudiante user ID
            format: Report format (pdf, html, json)
        
        Returns:
            Report with content, filename, and content_type
        """
        from app.factories import ReportFactory  # Import from __init__.py to ensure generators are registered
        
        estudiante = await self.user_service.get_user_by_id(estudiante_id)
        if not estudiante:
            raise ValueError("Estudiante not found")
        
        # Get enrollments with eager-loaded subject relationships (batch query)
        enrollments = await self.enrollment_repo.get_many_with_relations(
            estudiante_id=estudiante_id,
            relations=['subject']
        )
        
        # Build report data
        report_data = await self._build_student_report_data(estudiante, enrollments)
        
        # Calculate general average
        self._calculate_general_average(report_data)
        
        # Use Factory Method to generate report
        generator = ReportFactory.create_generator(format)
        return generator.generate(report_data)

