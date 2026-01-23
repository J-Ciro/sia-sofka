"""Estudiante service with estudiante-specific business logic."""

from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.services.user_service import UserService
from app.services.grade_service import GradeService
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.subject_repository import SubjectRepository
from app.schemas.user import UserUpdate


class EstudianteService:
    """Service for estudiante-specific business logic."""
    
    def __init__(self, db: AsyncSession, estudiante_user: User):
        """Initialize estudiante service.
        
        Args:
            db: Database session
            estudiante_user: Estudiante user instance
        """
        self.db = db
        self.estudiante_user = estudiante_user
        self.user_service = UserService(db)
        self.grade_service = GradeService(db)
        self.enrollment_repo = EnrollmentRepository(db)
        self.subject_repo = SubjectRepository(db)
    
    async def get_all_enrollments(self) -> list:
        """Get all enrollments for this estudiante.
        
        Returns:
            List of enrollments with subject information
        """
        # Get enrollments with eager-loaded subject relationships (batch query)
        enrollments = await self.enrollment_repo.get_many_with_relations(
            estudiante_id=self.estudiante_user.id,
            relations=['subject']
        )
        
        # Build result with already-loaded subjects
        result = []
        for enrollment in enrollments:
            if hasattr(enrollment, 'subject') and enrollment.subject:
                result.append({
                    "enrollment": enrollment,
                    "subject": enrollment.subject,
                })
        
        return result
    
    async def get_grades_by_subject(self, subject_id: int) -> list:
        """Get grades for this estudiante in a specific subject.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            List of grades
        
        Raises:
            ValueError: If estudiante is not enrolled in this subject
        """
        # Verify enrollment
        enrollment = await self.enrollment_repo.get_by_estudiante_and_subject(
            self.estudiante_user.id, subject_id
        )
        
        if not enrollment:
            raise ValueError("Estudiante is not enrolled in this subject")
        
        return await self.grade_service.get_grades_by_enrollment(enrollment.id)
    
    async def get_subject_status(self, subject_id: int) -> dict:
        """Get complete status of a subject for this estudiante.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            Dictionary with subject, enrollment, grades, and average
        
        Raises:
            ValueError: If estudiante is not enrolled in this subject
        """
        # Verify enrollment
        enrollment = await self.enrollment_repo.get_by_estudiante_and_subject(
            self.estudiante_user.id, subject_id
        )
        
        if not enrollment:
            raise ValueError("Estudiante is not enrolled in this subject")
        
        # Get subject
        subject = await self.subject_repo.get_by_id(subject_id)
        
        # Get grades
        grades = await self.grade_service.get_grades_by_enrollment(enrollment.id)
        
        # Calculate average
        try:
            average = await self.grade_service.calculate_average(enrollment.id)
        except ValueError:
            average = None
        
        return {
            "subject": subject,
            "enrollment": enrollment,
            "grades": grades,
            "average": float(average) if average else None,
        }
    
    async def _build_general_report_data(self, enrollments) -> dict:
        """Build report data structure for general report.
        
        Args:
            enrollments: List of enrollments with loaded subjects
        
        Returns:
            Dictionary with report data structure
        """
        report_data = {
            "estudiante": {
                "id": self.estudiante_user.id,
                "nombre": self.estudiante_user.nombre,
                "apellido": self.estudiante_user.apellido,
                "codigo_institucional": self.estudiante_user.codigo_institucional,
                "programa_academico": self.estudiante_user.programa_academico,
            },
            "subjects": [],
        }  # type: dict[str, Any]
        
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
    
    def _calculate_weighted_average(self, report_data: dict) -> None:
        """Calculate and add general weighted average to report data.
        
        Args:
            report_data: Report data dictionary (modified in place)
        """
        from decimal import Decimal
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
    
    async def generate_general_report(self, format: str = "pdf") -> dict:
        """Generate general report with all subjects and grades using Factory Method.
        
        Args:
            format: Report format (pdf, html, json)
        
        Returns:
            Report with content, filename, and content_type
        """
        from app.factories import ReportFactory  # Import from __init__.py to ensure generators are registered
        
        # Get enrollments with eager-loaded subject relationships (batch query)
        enrollments = await self.enrollment_repo.get_many_with_relations(
            estudiante_id=self.estudiante_user.id,
            relations=['subject']
        )
        
        # Build report data
        report_data = await self._build_general_report_data(enrollments)
        
        # Calculate general average
        self._calculate_weighted_average(report_data)
        
        # Use Factory Method to generate report
        generator = ReportFactory.create_generator(format)
        return generator.generate(report_data)
    
    async def update_profile(self, user_data: UserUpdate) -> User:
        """Update estudiante's own profile.
        
        Args:
            user_data: User update data
        
        Returns:
            Updated estudiante
        
        Raises:
            NotFoundError: If user not found
        """
        updated = await self.user_service.update_user(int(self.estudiante_user.id), user_data)
        if not updated:
            raise NotFoundError("User", int(self.estudiante_user.id))
        return updated

