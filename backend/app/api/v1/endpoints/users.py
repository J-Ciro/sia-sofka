"""User endpoints - Refactored to use services directly."""

from io import BytesIO
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User, UserRole
from app.schemas.bulk_import import BulkImportResult
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.admin_service import AdminService
from app.services.bulk_import_service import BulkImportService
from app.services.user_service import UserService
from app.api.v1.dependencies import require_admin

router = APIRouter()

EXCEL_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new user (Admin only)."""
    admin_service = AdminService(db, current_user)
    
    # Map role to creation method
    role_creators = {
        UserRole.ESTUDIANTE: admin_service.create_estudiante,
        UserRole.PROFESOR: admin_service.create_profesor,
    }
    
    try:
        creator = role_creators.get(user_data.role)
        if not creator:
            raise ValidationError("Invalid role for user creation")
        user = await creator(user_data)
        return user
    except ValueError as e:
        raise ValidationError(str(e))


@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all users (Admin only)."""
    user_service = UserService(db)
    estudiantes = await user_service.get_users_by_role(UserRole.ESTUDIANTE.value, skip, limit)
    profesores = await user_service.get_users_by_role(UserRole.PROFESOR.value, skip, limit)
    return list(estudiantes) + list(profesores)


@router.post("/bulk-import", response_model=BulkImportResult)
async def bulk_import_users(
    file: UploadFile = File(..., description="Archivo .xlsx con estudiantes"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Import students from Excel (Admin only). Upsert by email. Max 1000 rows, 5 MB."""
    if not (file.filename and file.filename.lower().endswith(".xlsx")):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .xlsx")
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="El archivo supera el límite de 5 MB")
    svc = BulkImportService(db)
    try:
        rows = svc.parse_excel(BytesIO(content))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    valid, errs = svc.validate_rows(rows)
    if errs:
        return Response(
            content=BulkImportResult(created=0, updated=0, errors=errs).model_dump_json(),
            status_code=400,
            media_type="application/json",
        )
    result = await svc.bulk_import_students(valid)
    return result


@router.get("/export")
async def export_users(
    role: str | None = Query(None, description="Filtrar por rol, ej. Estudiante"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Export users to Excel (Admin only). Excludes passwords."""
    svc = BulkImportService(db)
    buf = await svc.export_users_to_excel(role=role)
    return Response(
        content=buf.getvalue(),
        media_type=EXCEL_MIME,
        headers={"Content-Disposition": "attachment; filename=usuarios.xlsx"},
    )


@router.get("/template")
async def download_import_template(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Download Excel template for bulk import (Admin only)."""
    svc = BulkImportService(db)
    buf = svc.generate_import_template()
    return Response(
        content=buf.getvalue(),
        media_type=EXCEL_MIME,
        headers={"Content-Disposition": "attachment; filename=plantilla_estudiantes.xlsx"},
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get user by ID (Admin only)."""
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise NotFoundError("User", user_id)
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update user (Admin only)."""
    admin_service = AdminService(db, current_user)
    user = await admin_service.update_user(user_id, user_data)
    
    if not user:
        raise NotFoundError("User", user_id)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete user (Admin only)."""
    admin_service = AdminService(db, current_user)
    deleted = await admin_service.delete_user(user_id)
    
    if not deleted:
        raise NotFoundError("User", user_id)

