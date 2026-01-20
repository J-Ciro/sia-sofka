"""Repositories package."""

from app.repositories.base import AbstractRepository
from app.repositories.user_repository import UserRepository
from app.repositories.subject_repository import SubjectRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.grade_repository import GradeRepository
from app.repositories.schedule_repository import ScheduleRepository

__all__ = [
    "AbstractRepository",
    "UserRepository",
    "SubjectRepository",
    "EnrollmentRepository",
    "GradeRepository",
    "ScheduleRepository",
]
