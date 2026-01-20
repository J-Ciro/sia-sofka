"""API v1 package."""

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    subjects,
    enrollments,
    grades,
    reports,
    profile,
    attendance,
    schedules,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(subjects.router, prefix="/subjects", tags=["subjects"])
api_router.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
api_router.include_router(grades.router, prefix="/grades", tags=["grades"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(profile.router, prefix="/profile", tags=["profile"])
api_router.include_router(attendance.router, prefix="/attendance", tags=["attendance"])
api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])
