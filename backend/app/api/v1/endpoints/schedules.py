"""Schedule endpoints - TASK-014 a TASK-018. Horarios y calendario.

Enhanced for Task 5.1: Extended endpoints to support date-specific schedules
- Modified POST endpoint to accept fecha_especifica field
- Added GET endpoint for date range queries
- Enhanced existing endpoints to return date information
"""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError, ForbiddenError, ScheduleConflictError
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.services.schedule_service import ScheduleService
from app.api.v1.dependencies import get_current_active_user, require_admin, require_admin_or_profesor

router = APIRouter()


def _to_response(s) -> ScheduleResponse:
    """Convert Schedule to ScheduleResponse, handling both regular and virtual schedules."""
    # For virtual schedules (detached from session), ensure clean serialization
    if hasattr(s, '_sa_instance_state') and s._sa_instance_state is None:
        # Virtual schedule - create dict manually to avoid SQLAlchemy serialization issues
        data = {
            'id': s.id,
            'codigo': s.codigo,
            'subject_id': s.subject_id,
            'classroom_id': s.classroom_id,
            'dia_semana': s.dia_semana,
            'hora_inicio': s.hora_inicio,
            'hora_fin': s.hora_fin,
            'fecha_especifica': s.fecha_especifica,
        }
        # Handle nested relationships - convert to dict if they exist
        if hasattr(s, 'subject') and s.subject is not None:
            from app.schemas.schedule import SubjectNested
            try:
                # Try to serialize subject using Pydantic
                data['subject'] = SubjectNested.model_validate(s.subject, from_attributes=True)
            except Exception:
                # Fallback: create dict manually with all required fields
                subject_data = {
                    'id': s.subject.id,
                    'nombre': s.subject.nombre,
                    'codigo_institucional': getattr(s.subject, 'codigo_institucional', ''),
                    'profesor_id': getattr(s.subject, 'profesor_id', 0),
                }
                # Add profesor nested if available
                if hasattr(s.subject, 'profesor') and s.subject.profesor is not None:
                    from app.schemas.schedule import ProfesorNested
                    try:
                        subject_data['profesor'] = ProfesorNested.model_validate(s.subject.profesor, from_attributes=True)
                    except Exception:
                        subject_data['profesor'] = {
                            'id': s.subject.profesor.id,
                            'nombre': getattr(s.subject.profesor, 'nombre', ''),
                            'apellido': getattr(s.subject.profesor, 'apellido', ''),
                        }
                data['subject'] = subject_data
        if hasattr(s, 'classroom') and s.classroom is not None:
            from app.schemas.schedule import ClassroomNested
            try:
                # Try to serialize classroom using Pydantic
                data['classroom'] = ClassroomNested.model_validate(s.classroom, from_attributes=True)
            except Exception:
                # Fallback: create dict manually with all required fields
                data['classroom'] = {
                    'id': s.classroom.id,
                    'codigo': s.classroom.codigo,
                    'nombre': s.classroom.nombre,
                    'capacidad': getattr(s.classroom, 'capacidad', 0),
                    'ubicacion': getattr(s.classroom, 'ubicacion', None),
                }
        return ScheduleResponse.model_validate(data)
    else:
        # Regular schedule - standard serialization
        try:
            return ScheduleResponse.model_validate(s, from_attributes=True)
        except Exception as e:
            # Fallback for regular schedules too
            data = {
                'id': s.id,
                'codigo': s.codigo,
                'subject_id': s.subject_id,
                'classroom_id': s.classroom_id,
                'dia_semana': s.dia_semana,
                'hora_inicio': s.hora_inicio,
                'hora_fin': s.hora_fin,
                'fecha_especifica': getattr(s, 'fecha_especifica', None),
            }
            if hasattr(s, 'subject') and s.subject is not None:
                from app.schemas.schedule import SubjectNested
                try:
                    data['subject'] = SubjectNested.model_validate(s.subject, from_attributes=True)
                except Exception:
                    # Fallback: create dict manually with all required fields
                    subject_data = {
                        'id': s.subject.id,
                        'nombre': s.subject.nombre,
                        'codigo_institucional': getattr(s.subject, 'codigo_institucional', ''),
                        'profesor_id': getattr(s.subject, 'profesor_id', 0),
                    }
                    # Add profesor nested if available
                    if hasattr(s.subject, 'profesor') and s.subject.profesor is not None:
                        from app.schemas.schedule import ProfesorNested
                        try:
                            subject_data['profesor'] = ProfesorNested.model_validate(s.subject.profesor, from_attributes=True)
                        except Exception:
                            subject_data['profesor'] = {
                                'id': s.subject.profesor.id,
                                'nombre': getattr(s.subject.profesor, 'nombre', ''),
                                'apellido': getattr(s.subject.profesor, 'apellido', ''),
                            }
                    data['subject'] = subject_data
            if hasattr(s, 'classroom') and s.classroom is not None:
                from app.schemas.schedule import ClassroomNested
                try:
                    data['classroom'] = ClassroomNested.model_validate(s.classroom, from_attributes=True)
                except Exception:
                    # Fallback: create dict manually with all required fields
                    data['classroom'] = {
                        'id': s.classroom.id,
                        'codigo': s.classroom.codigo,
                        'nombre': s.classroom.nombre,
                        'capacidad': getattr(s.classroom, 'capacidad', 0),
                        'ubicacion': getattr(s.classroom, 'ubicacion', None),
                    }
            return ScheduleResponse.model_validate(data)


# POST /api/v1/schedules - TASK-014 (Enhanced for Task 5.1)
@router.post("", response_model=ScheduleResponse, status_code=status.HTTP_201_CREATED)
async def create_schedule(
    data: ScheduleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Crear horario (Admin o Profesor). Profesor solo para sus materias; elige aula del banco. Valida conflictos.
    
    Enhanced for Task 5.1: Now accepts optional fecha_especifica field for date-specific schedules.
    When fecha_especifica is provided, the schedule will be created only for that specific date
    rather than as a recurring weekly pattern.
    """
    if current_user.role == UserRole.PROFESOR:
        r = await db.execute(select(Subject).where(Subject.id == data.subject_id))
        sub = r.scalar_one_or_none()
        if not sub or sub.profesor_id != current_user.id:
            raise ForbiddenError("Solo puedes asignar horarios a tus propias materias")
    service = ScheduleService(db)
    try:
        schedule = await service.create_schedule(data)
        return _to_response(schedule)
    except ValueError as e:
        error_msg = str(e)
        if error_msg == "Subject not found":
            raise ValidationError("Subject not found")
        # Convert other ValueError (like validation errors from Pydantic) to ValidationError
        # This ensures proper HTTP status code (400) and error message display
        raise ValidationError(error_msg)
    except ScheduleConflictError:
        # Re-raise conflict errors as-is (they have proper 422 status)
        raise


# GET /api/v1/schedules/weekly - TASK-015
@router.get("/weekly", response_model=List[ScheduleResponse])
async def get_weekly_schedules(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    user_id: Optional[int] = Query(None, description="Admin: ver otro usuario"),
    role: Optional[UserRole] = Query(None, description="Admin: rol al ver otro usuario"),
):
    """Horario semanal. Profesor/Estudiante: el propio. Admin: todos; o user_id+role para filtrar."""
    service = ScheduleService(db)
    uid = current_user.id
    r = current_user.role

    if current_user.role == UserRole.ADMIN and user_id is not None:
        uid = int(user_id)
        r = role if role is not None else current_user.role

    if r == UserRole.PROFESOR:
        rows = await service.get_professor_schedule(int(uid))
    elif r == UserRole.ESTUDIANTE:
        rows = await service.get_student_schedule(int(uid))
    elif r == UserRole.ADMIN and user_id is not None and role is not None:
        if role == UserRole.PROFESOR:
            rows = await service.get_professor_schedule(int(uid))
        elif role == UserRole.ESTUDIANTE:
            rows = await service.get_student_schedule(int(uid))
        else:
            rows = []
    elif current_user.role == UserRole.ADMIN and user_id is None:
        rows = await service.get_all_schedules()
    else:
        rows = []

    return [_to_response(s) for s in rows]


# GET /api/v1/schedules/date-range - NEW for Task 5.1
@router.get("/date-range", response_model=List[ScheduleResponse])
async def get_schedules_by_date_range(
    start_date: date = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    end_date: date = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    user_id: Optional[int] = Query(None, description="Admin: ver otro usuario"),
    role: Optional[UserRole] = Query(None, description="Admin: rol al ver otro usuario"),
):
    """Obtener horarios para un rango de fechas específico.
    
    Este endpoint devuelve horarios para un rango de fechas, incluyendo:
    - Horarios específicos de fecha que caen dentro del rango
    - Horarios semanales recurrentes expandidos a fechas específicas dentro del rango
    
    Útil para vistas de calendario mensual y navegación por fechas.
    Profesor/Estudiante: sus propios horarios. Admin: todos; o user_id+role para filtrar.
    """
    # Validate date range
    if start_date > end_date:
        raise ValidationError("La fecha de inicio debe ser anterior o igual a la fecha de fin")
    
    # Limit range to prevent excessive queries (e.g., max 3 months)
    from datetime import timedelta
    max_range = timedelta(days=93)  # ~3 months
    if end_date - start_date > max_range:
        raise ValidationError("El rango de fechas no puede ser mayor a 3 meses")
    
    service = ScheduleService(db)
    uid = current_user.id
    r = current_user.role

    # Handle admin user filtering
    if current_user.role == UserRole.ADMIN and user_id is not None:
        uid = int(user_id)
        r = role if role is not None else current_user.role

    # Get schedules for calendar display (expanded to specific dates)
    if r == UserRole.PROFESOR:
        schedules = await service.get_schedules_for_calendar(
            start_date, end_date, int(uid), UserRole.PROFESOR
        )
    elif r == UserRole.ESTUDIANTE:
        schedules = await service.get_schedules_for_calendar(
            start_date, end_date, int(uid), UserRole.ESTUDIANTE
        )
    elif current_user.role == UserRole.ADMIN:
        # Admin can see all schedules or filtered by user_id/role
        filter_uid = int(uid) if user_id is not None else None
        filter_role = r if user_id is not None and role is not None else None
        schedules = await service.get_schedules_for_calendar(
            start_date, end_date, filter_uid, filter_role
        )
    else:
        schedules = []

    try:
        return [_to_response(s) for s in schedules]
    except Exception as e:
        import traceback
        print(f"Error serializing schedules: {e}")
        print(traceback.format_exc())
        # Try to return at least basic data
        result = []
        for s in schedules:
            try:
                result.append(_to_response(s))
            except Exception as inner_e:
                print(f"Error serializing schedule {getattr(s, 'id', 'unknown')}: {inner_e}")
                # Skip this schedule if it can't be serialized
                continue
        return result


# PUT /api/v1/schedules/{schedule_id} - TASK-016 (Enhanced for Task 5.1)
@router.put("/{schedule_id}", response_model=ScheduleResponse)
async def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Actualizar horario (Admin o Profesor). Profesor solo puede actualizar sus propios horarios. Valida conflictos.
    
    Enhanced for Task 5.1: Now supports updating fecha_especifica field for converting
    between weekly recurring and date-specific schedules.
    """
    service = ScheduleService(db)
    
    # If user is a professor, verify they own the schedule
    if current_user.role == UserRole.PROFESOR:
        existing_schedule = await service.get_by_id(schedule_id)
        if not existing_schedule:
            raise NotFoundError("Schedule", schedule_id)
        
        # Get the subject to check if it belongs to the professor
        r = await db.execute(select(Subject).where(Subject.id == existing_schedule.subject_id))
        subject = r.scalar_one_or_none()
        if not subject or subject.profesor_id != current_user.id:
            raise ForbiddenError("Solo puedes actualizar horarios de tus propias materias")
    
    try:
        s = await service.update_schedule(schedule_id, data)
        if not s:
            raise NotFoundError("Schedule", schedule_id)
        return _to_response(s)
    except ValueError:
        raise

# PATCH /api/v1/schedules/{schedule_id}/move - NEW for Task 5.1 (Drag & Drop support)
@router.patch("/{schedule_id}/move", response_model=ScheduleResponse)
async def move_schedule(
    schedule_id: int,
    new_date: date = Query(..., description="Nueva fecha (YYYY-MM-DD)"),
    new_start_time: str = Query(..., description="Nueva hora de inicio (HH:MM)"),
    new_end_time: str = Query(..., description="Nueva hora de fin (HH:MM)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Mover horario a nueva fecha y hora (útil para drag & drop).
    
    Este endpoint está optimizado para operaciones de arrastrar y soltar en el calendario.
    Actualiza la fecha específica, día de la semana y horarios de un schedule existente.
    Admin puede mover cualquier horario. Profesor solo puede mover sus propios horarios.
    """
    from datetime import time
    
    service = ScheduleService(db)
    
    # If user is a professor, verify they own the schedule
    if current_user.role == UserRole.PROFESOR:
        existing_schedule = await service.get_by_id(schedule_id)
        if not existing_schedule:
            raise NotFoundError("Schedule", schedule_id)
        
        # Get the subject to check if it belongs to the professor
        r = await db.execute(select(Subject).where(Subject.id == existing_schedule.subject_id))
        subject = r.scalar_one_or_none()
        if not subject or subject.profesor_id != current_user.id:
            raise ForbiddenError("Solo puedes mover horarios de tus propias materias")
    
    try:
        # Parse time strings
        start_hour, start_min = map(int, new_start_time.split(':'))
        end_hour, end_min = map(int, new_end_time.split(':'))
        start_time = time(start_hour, start_min)
        end_time = time(end_hour, end_min)
        
        # Calculate day of week from new date
        new_day_of_week = new_date.weekday() + 1  # Convert to 1-6 format
        if new_day_of_week == 7:  # Sunday
            raise ValidationError("No se permiten horarios los domingos")
        
        # Create update data
        update_data = ScheduleUpdate(
            fecha_especifica=new_date,
            dia_semana=new_day_of_week,
            hora_inicio=start_time,
            hora_fin=end_time,
        )
        
        s = await service.update_schedule(schedule_id, update_data)
        if not s:
            raise NotFoundError("Schedule", schedule_id)
        return _to_response(s)
        
    except ValueError as e:
        if "invalid literal" in str(e) or "does not match format" in str(e):
            raise ValidationError("Formato de hora inválido. Use HH:MM")
        raise ValidationError(str(e))


# DELETE /api/v1/schedules/{schedule_id} - TASK-017
@router.delete("/{schedule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_schedule(
    schedule_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Eliminar horario (Admin)."""
    service = ScheduleService(db)
    ok = await service.delete_schedule(schedule_id)
    if not ok:
        raise NotFoundError("Schedule", schedule_id)


# GET /api/v1/schedules/classroom/{classroom_id} - TASK-018 (Enhanced for Task 5.1)
@router.get("/classroom/{classroom_id}", response_model=List[ScheduleResponse])
async def get_schedules_by_classroom(
    classroom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Horarios de un aula.
    
    Enhanced for Task 5.1: Returns both weekly recurring and date-specific schedules
    with complete date information for calendar display.
    """
    service = ScheduleService(db)
    rows = await service.get_by_classroom(classroom_id)
    return [_to_response(s) for s in rows]
