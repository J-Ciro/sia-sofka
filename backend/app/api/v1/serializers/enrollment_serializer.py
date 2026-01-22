"""Enrollment serializer for API responses."""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.enrollment import Enrollment
from app.models.user import User
from app.models.subject import Subject
from app.schemas.enrollment import (
    EnrollmentResponse,
    EstudianteInfo,
    SubjectInfo,
)


class EnrollmentSerializer:
    """Serializer for Enrollment entities with efficient batch loading."""

    @staticmethod
    async def serialize_batch(
        enrollments: List[Enrollment], db: AsyncSession
    ) -> List[EnrollmentResponse]:
        """Serialize a batch of enrollments with efficient batch loading of relationships.
        
        This method loads all estudiante and subject relationships in batches
        to avoid N+1 queries.
        
        Args:
            enrollments: List of Enrollment entities to serialize
            db: Database session
            
        Returns:
            List of EnrollmentResponse objects
        """
        if not enrollments:
            return []

        # Collect all unique estudiante_ids and subject_ids
        unique_estudiante_ids = set()
        unique_subject_ids = set()

        for enrollment in enrollments:
            unique_estudiante_ids.add(enrollment.estudiante_id)
            unique_subject_ids.add(enrollment.subject_id)

        # Batch load all estudiantes
        estudiantes_map = {}
        if unique_estudiante_ids:
            estudiantes_stmt = select(User).where(User.id.in_(list(unique_estudiante_ids)))
            estudiantes_result = await db.execute(estudiantes_stmt)
            estudiantes_list = estudiantes_result.scalars().all()
            estudiantes_map = {est.id: est for est in estudiantes_list}

        # Batch load all subjects
        subjects_map = {}
        if unique_subject_ids:
            subjects_stmt = select(Subject).where(Subject.id.in_(list(unique_subject_ids)))
            subjects_result = await db.execute(subjects_stmt)
            subjects_list = subjects_result.scalars().all()
            subjects_map = {subj.id: subj for subj in subjects_list}

        # Serialize each enrollment using batch-loaded maps
        responses = []
        for enrollment in enrollments:
            # Get estudiante from batch-loaded map
            estudiante_info = None
            if enrollment.estudiante_id in estudiantes_map:
                estudiante = estudiantes_map[enrollment.estudiante_id]
                estudiante_info = EstudianteInfo(
                    id=estudiante.id,
                    nombre=estudiante.nombre,
                    apellido=estudiante.apellido,
                    codigo_institucional=estudiante.codigo_institucional,
                    email=estudiante.email,
                )

            # Get subject from batch-loaded map
            subject_info = None
            if enrollment.subject_id in subjects_map:
                subject = subjects_map[enrollment.subject_id]
                subject_info = SubjectInfo(
                    id=subject.id,
                    nombre=subject.nombre,
                    codigo_institucional=subject.codigo_institucional,
                    numero_creditos=subject.numero_creditos,
                )

            responses.append(
                EnrollmentResponse(
                    id=enrollment.id,
                    estudiante_id=enrollment.estudiante_id,
                    subject_id=enrollment.subject_id,
                    created_at=enrollment.created_at,
                    estudiante=estudiante_info,
                    subject=subject_info,
                )
            )

        return responses

