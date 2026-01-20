"""Simple async integration tests for Attendance endpoints.

Uses dependency overrides to test endpoints without JWT authentication.
"""

import pytest
from datetime import datetime, date
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.main import app
from app.models.user import User, UserRole
from app.models.attendance import AttendanceStatus, Attendance, ClaseSession
from app.models.enrollment import Enrollment
from app.models.subject import Subject


@pytest.fixture
async def test_profesor(async_db_session: AsyncSession):
    """Create a test profesor user."""
    from bcrypt import hashpw, gensalt
    profesor = User(
        email="test_prof_async@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Test",
        apellido="Profesor",
        codigo_institucional="PRFASYNC",
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    return profesor


@pytest.fixture
async def test_subject_async(async_db_session: AsyncSession, test_profesor: User):
    """Create a test subject."""
    subject = Subject(
        nombre="Async Test Subject",
        codigo_institucional="ASYNC001",
        numero_creditos=3,
        profesor_id=test_profesor.id,
    )
    async_db_session.add(subject)
    await async_db_session.commit()
    await async_db_session.refresh(subject)
    return subject


@pytest.fixture
async def test_student_async(async_db_session: AsyncSession):
    """Create a test student."""
    from bcrypt import hashpw, gensalt
    student = User(
        email="test_student_async@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.ESTUDIANTE,
        nombre="Test",
        apellido="Student",
        codigo_institucional="ESTASYNC",
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(student)
    await async_db_session.commit()
    await async_db_session.refresh(student)
    return student


@pytest.fixture
async def async_client_with_auth(async_db_session: AsyncSession, test_profesor: User):
    """Create async client with authentication override."""
    from app.api.v1.dependencies import get_db, get_current_user
    
    async def override_get_db():
        yield async_db_session
    
    async def override_get_current_user():
        return test_profesor
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_clase_session_endpoint_success(
    async_client_with_auth: AsyncClient,
    test_subject_async: Subject
):
    """Test POST /api/v1/attendance/sessions endpoint successfully."""
    today = date.today()
    payload = {
        "subject_id": test_subject_async.id,
        "fecha": str(today),
        "hora_inicio": f"{today}T08:00:00",
        "hora_fin": f"{today}T10:00:00",
        "descripcion": "Test session",
    }
    
    response = await async_client_with_auth.post(
        "/api/v1/attendance/sessions",
        json=payload
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["subject_id"] == test_subject_async.id
    assert "id" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_clase_session_endpoint_validation_error(
    async_client_with_auth: AsyncClient,
    test_subject_async: Subject
):
    """Test POST /api/v1/attendance/sessions with validation error."""
    today = date.today()
    payload = {
        "subject_id": test_subject_async.id,
        "fecha": str(today),
        "hora_inicio": f"{today}T10:00:00",
        "hora_fin": f"{today}T08:00:00",  # Invalid: end before start
        "descripcion": "Invalid session",
    }
    
    response = await async_client_with_auth.post(
        "/api/v1/attendance/sessions",
        json=payload
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_clase_sessions_endpoint(
    async_client_with_auth: AsyncClient,
    async_db_session: AsyncSession,
    test_subject_async: Subject,
    test_profesor: User
):
    """Test GET /api/v1/attendance/sessions endpoint."""
    # Create a session first
    today = date.today()
    session = ClaseSession(
        subject_id=test_subject_async.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=test_profesor.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    
    response = await async_client_with_auth.get("/api/v1/attendance/sessions")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_clase_session_endpoint(
    async_client_with_auth: AsyncClient,
    async_db_session: AsyncSession,
    test_subject_async: Subject,
    test_profesor: User
):
    """Test GET /api/v1/attendance/sessions/{id} endpoint."""
    today = date.today()
    session = ClaseSession(
        subject_id=test_subject_async.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=test_profesor.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    response = await async_client_with_auth.get(
        f"/api/v1/attendance/sessions/{session.id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session.id


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_clase_session_not_found(async_client_with_auth: AsyncClient):
    """Test GET /api/v1/attendance/sessions/{id} with non-existent ID."""
    response = await async_client_with_auth.get("/api/v1/attendance/sessions/99999")
    
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_session_attendances_endpoint(
    async_client_with_auth: AsyncClient,
    async_db_session: AsyncSession,
    test_subject_async: Subject,
    test_profesor: User,
    test_student_async: User
):
    """Test GET /api/v1/attendance/sessions/{id}/attendances endpoint."""
    today = date.today()
    session = ClaseSession(
        subject_id=test_subject_async.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=test_profesor.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    # Create attendance
    attendance = Attendance(
        clase_session_id=session.id,
        estudiante_id=test_student_async.id,
        estado=AttendanceStatus.PRESENTE,
    )
    async_db_session.add(attendance)
    await async_db_session.commit()
    
    response = await async_client_with_auth.get(
        f"/api/v1/attendance/sessions/{session.id}/attendances"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_session_attendances_endpoint(
    async_client_with_auth: AsyncClient,
    async_db_session: AsyncSession,
    test_subject_async: Subject,
    test_profesor: User,
    test_student_async: User
):
    """Test POST /api/v1/attendance/sessions/{id}/save endpoint."""
    today = date.today()
    session = ClaseSession(
        subject_id=test_subject_async.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=test_profesor.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    # Create enrollment
    enrollment = Enrollment(
        estudiante_id=test_student_async.id,
        subject_id=test_subject_async.id,
    )
    async_db_session.add(enrollment)
    await async_db_session.commit()
    
    # Create initial attendance
    attendance = Attendance(
        clase_session_id=session.id,
        estudiante_id=test_student_async.id,
        estado=AttendanceStatus.AUSENTE,
    )
    async_db_session.add(attendance)
    await async_db_session.commit()
    await async_db_session.refresh(attendance)
    
    payload = [
        {
            "estudiante_id": test_student_async.id,
            "estado": "PRESENTE"
        }
    ]
    
    response = await async_client_with_auth.post(
        f"/api/v1/attendance/sessions/{session.id}/save",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "updated_count" in data


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_session_statistics_endpoint(
    async_client_with_auth: AsyncClient,
    async_db_session: AsyncSession,
    test_subject_async: Subject,
    test_profesor: User,
    test_student_async: User
):
    """Test GET /api/v1/attendance/sessions/{id}/stats endpoint."""
    today = date.today()
    session = ClaseSession(
        subject_id=test_subject_async.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=test_profesor.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    # Create attendance
    attendance = Attendance(
        clase_session_id=session.id,
        estudiante_id=test_student_async.id,
        estado=AttendanceStatus.PRESENTE,
    )
    async_db_session.add(attendance)
    await async_db_session.commit()
    
    response = await async_client_with_auth.get(
        f"/api/v1/attendance/sessions/{session.id}/stats"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "presentes" in data
    assert "porcentaje_asistencia" in data


@pytest.fixture
async def async_client_student_auth(async_db_session: AsyncSession, test_student_async: User):
    """Create async client with student authentication."""
    from app.api.v1.dependencies import get_db, get_current_user
    
    async def override_get_db():
        yield async_db_session
    
    async def override_get_current_user():
        return test_student_async
    
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_clase_session_unauthorized_student(
    async_client_student_auth: AsyncClient,
    test_subject_async: Subject
):
    """Test POST /api/v1/attendance/sessions with student (should fail)."""
    today = date.today()
    payload = {
        "subject_id": test_subject_async.id,
        "fecha": str(today),
        "hora_inicio": f"{today}T08:00:00",
        "hora_fin": f"{today}T10:00:00",
    }
    
    response = await async_client_student_auth.post(
        "/api/v1/attendance/sessions",
        json=payload
    )
    
    # UnauthorizedError is raised before try/except, so it returns 401
    # But it might be caught and converted to 400 in the except block
    assert response.status_code in [400, 401]


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_clase_session_duplicate(
    async_client_with_auth: AsyncClient,
    async_db_session: AsyncSession,
    test_subject_async: Subject,
    test_profesor: User
):
    """Test POST /api/v1/attendance/sessions with duplicate session."""
    today = date.today()
    
    # Create first session
    session = ClaseSession(
        subject_id=test_subject_async.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=test_profesor.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    
    # Try to create duplicate
    payload = {
        "subject_id": test_subject_async.id,
        "fecha": str(today),
        "hora_inicio": f"{today}T08:00:00",
        "hora_fin": f"{today}T10:00:00",
        "descripcion": "Duplicate session",
    }
    
    response = await async_client_with_auth.post(
        "/api/v1/attendance/sessions",
        json=payload
    )
    
    assert response.status_code == 400


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_clase_sessions_with_subject_filter(
    async_client_with_auth: AsyncClient,
    async_db_session: AsyncSession,
    test_subject_async: Subject,
    test_profesor: User
):
    """Test GET /api/v1/attendance/sessions with subject_id filter."""
    today = date.today()
    session = ClaseSession(
        subject_id=test_subject_async.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=test_profesor.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    
    response = await async_client_with_auth.get(
        "/api/v1/attendance/sessions",
        params={"subject_id": test_subject_async.id}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_save_session_attendances_not_found(
    async_client_with_auth: AsyncClient
):
    """Test POST /api/v1/attendance/sessions/{id}/save with non-existent session."""
    payload = [{"estudiante_id": 1, "estado": "PRESENTE"}]
    
    response = await async_client_with_auth.post(
        "/api/v1/attendance/sessions/99999/save",
        json=payload
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_session_statistics_not_found(async_client_with_auth: AsyncClient):
    """Test GET /api/v1/attendance/sessions/{id}/stats with non-existent session."""
    response = await async_client_with_auth.get("/api/v1/attendance/sessions/99999/stats")
    
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_attendance_endpoint(
    async_client_with_auth: AsyncClient,
    async_db_session: AsyncSession,
    test_subject_async: Subject,
    test_profesor: User,
    test_student_async: User
):
    """Test PATCH /api/v1/attendance/{id} endpoint."""
    today = date.today()
    session = ClaseSession(
        subject_id=test_subject_async.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=test_profesor.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    attendance = Attendance(
        clase_session_id=session.id,
        estudiante_id=test_student_async.id,
        estado=AttendanceStatus.AUSENTE,
    )
    async_db_session.add(attendance)
    await async_db_session.commit()
    await async_db_session.refresh(attendance)
    
    payload = {"estado": "PRESENTE"}
    
    response = await async_client_with_auth.patch(
        f"/api/v1/attendance/{attendance.id}",
        json=payload
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["estado"] == "PRESENTE"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_attendance_not_found(async_client_with_auth: AsyncClient):
    """Test PATCH /api/v1/attendance/{id} with non-existent attendance."""
    payload = {"estado": "PRESENTE"}
    
    response = await async_client_with_auth.patch(
        "/api/v1/attendance/99999",
        json=payload
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
@pytest.mark.integration
async def test_update_attendance_unauthorized_student(
    async_client_student_auth: AsyncClient,
    async_db_session: AsyncSession,
    test_subject_async: Subject,
    test_profesor: User,
    test_student_async: User
):
    """Test PATCH /api/v1/attendance/{id} with student (should fail)."""
    today = date.today()
    session = ClaseSession(
        subject_id=test_subject_async.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        creado_por=test_profesor.id,
    )
    async_db_session.add(session)
    await async_db_session.commit()
    await async_db_session.refresh(session)
    
    attendance = Attendance(
        clase_session_id=session.id,
        estudiante_id=test_student_async.id,
        estado=AttendanceStatus.AUSENTE,
    )
    async_db_session.add(attendance)
    await async_db_session.commit()
    await async_db_session.refresh(attendance)
    
    payload = {"estado": "PRESENTE"}
    
    response = await async_client_student_auth.patch(
        f"/api/v1/attendance/{attendance.id}",
        json=payload
    )
    
    assert response.status_code == 403
