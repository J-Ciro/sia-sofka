"""Schemas package."""

from app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse
from app.schemas.subject import SubjectBase, SubjectCreate, SubjectUpdate, SubjectResponse
from app.schemas.enrollment import EnrollmentBase, EnrollmentCreate, EnrollmentResponse
from app.schemas.grade import GradeBase, GradeCreate, GradeUpdate, GradeResponse
from app.schemas.token import Token, TokenData
from app.schemas.report import ReportRequest, ReportResponse
from app.schemas.attendance import (
    ClaseSessionCreate,
    ClaseSessionResponse,
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    SessionStatisticsResponse,
    AttendanceStatsResponse,
)

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "SubjectBase",
    "SubjectCreate",
    "SubjectUpdate",
    "SubjectResponse",
    "EnrollmentBase",
    "EnrollmentCreate",
    "EnrollmentResponse",
    "GradeBase",
    "GradeCreate",
    "GradeUpdate",
    "GradeResponse",
    "Token",
    "TokenData",
    "ReportRequest",
    "ReportResponse",
    "ClaseSessionCreate",
    "ClaseSessionResponse",
    "AttendanceCreate",
    "AttendanceUpdate",
    "AttendanceResponse",
    "SessionStatisticsResponse",
    "AttendanceStatsResponse",
]
