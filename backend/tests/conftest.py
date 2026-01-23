"""Pytest configuration and fixtures."""

import pytest
import os

# ===== ENVIRONMENT SETUP (BEFORE ANY IMPORTS) =====
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("DATABASE_URL_SYNC", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-testing-only-123456789012")
os.environ.setdefault("DEBUG", "false")

# ===== IMPORTS AFTER ENV SETUP =====
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as AsyncSessionType, async_sessionmaker
from datetime import date, datetime
from bcrypt import hashpw, gensalt
from httpx import AsyncClient, ASGITransport

# Import models (now safe because database.py uses lazy initialization)
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.attendance import ClaseSession
from app.models.schedule import Classroom, Schedule

# Import app and Base
from app.main import app
from app.core.database import Base

# Test database URL
TEST_DATABASE_URL_SYNC = "sqlite:///:memory:"


# ===== SYNC SESSION (for unit tests) =====
@pytest.fixture(scope="function")
def db_session():
    """Create a synchronous test database session for unit tests."""
    engine = create_engine(
        TEST_DATABASE_URL_SYNC,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = SessionLocal()
    yield session
    
    # Cleanup
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)


# ===== USER FIXTURES =====
@pytest.fixture
def admin_user(db_session):
    """Create a test admin user."""
    admin = User(
        email="admin@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional="ADM001",
        fecha_nacimiento=date(1990, 1, 1),
    )
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def profesor_user(db_session):
    """Create a test profesor user."""
    profesor = User(
        email="profesor@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Profesor",
        apellido="Test",
        codigo_institucional="PRF001",
        fecha_nacimiento=date(1985, 5, 15),
        area_ensenanza="Matemáticas",
    )
    db_session.add(profesor)
    db_session.commit()
    return profesor


@pytest.fixture
def estudiante_user(db_session):
    """Create a test estudiante user."""
    estudiante = User(
        email="estudiante@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante",
        apellido="Test",
        codigo_institucional="EST001",
        fecha_nacimiento=date(2005, 3, 20),
    )
    db_session.add(estudiante)
    db_session.commit()
    return estudiante


# ===== SUBJECT FIXTURES =====
@pytest.fixture
def subject(db_session, profesor_user):
    """Create a test subject."""
    subject_obj = Subject(
        nombre="Matemáticas Avanzadas",
        codigo_institucional="MAT301",
        numero_creditos=3,
        profesor_id=profesor_user.id,
        descripcion="Cálculo diferencial e integral",
    )
    db_session.add(subject_obj)
    db_session.commit()
    return subject_obj


# ===== ENROLLMENT FIXTURES =====
@pytest.fixture
def enrollment(db_session, estudiante_user, subject):
    """Create a test enrollment."""
    enrollment_obj = Enrollment(
        estudiante_id=estudiante_user.id,
        subject_id=subject.id,
    )
    db_session.add(enrollment_obj)
    db_session.commit()
    return enrollment_obj


# ===== CLASSROOM FIXTURES (horarios-calendario) =====
@pytest.fixture
def classroom(db_session):
    """Create a test classroom (aula) for schedules."""
    c = Classroom(
        codigo="AULA-301",
        nombre="Aula 301",
        capacidad=40,
        ubicacion="Edificio A, Tercer piso",
    )
    db_session.add(c)
    db_session.commit()
    return c


# ===== CLASE SESSION FIXTURES =====
@pytest.fixture
def clase_session(db_session, subject, profesor_user):
    """Create a test clase session."""
    clase = ClaseSession(
        subject_id=subject.id,
        fecha=date(2026, 1, 19),
        hora_inicio=datetime(2026, 1, 19, 8, 0),
        hora_fin=datetime(2026, 1, 19, 10, 0),
        descripcion="Clase de Cálculo Diferencial",
        creado_por=profesor_user.id,
    )
    db_session.add(clase)
    db_session.commit()
    return clase



# ===== ASYNC SESSION (for integration tests and schedule async unit tests) =====
@pytest.fixture(scope="function")
async def async_db_session():
    """Create an async test database session for integration tests."""
    TEST_DATABASE_URL_ASYNC = "sqlite+aiosqlite:///:memory:"
    
    engine = create_async_engine(
        TEST_DATABASE_URL_ASYNC,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    AsyncSessionLocal = async_sessionmaker(
        engine, 
        class_=AsyncSessionType, 
        expire_on_commit=False
    )
    
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()


# ===== ASYNC FIXTURES (schedule repo/service unit tests - async) =====
@pytest.fixture
async def async_profesor_user(async_db_session):
    """Profesor para tests async de schedules."""
    u = User(
        email="profesor@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.PROFESOR,
        nombre="Profesor",
        apellido="Test",
        codigo_institucional="PRF001",
        fecha_nacimiento=date(1985, 5, 15),
        area_ensenanza="Matemáticas",
    )
    async_db_session.add(u)
    await async_db_session.commit()
    await async_db_session.refresh(u)
    return u


@pytest.fixture
async def async_classroom(async_db_session):
    """Aula para tests async de schedules."""
    c = Classroom(
        codigo="AULA-301",
        nombre="Aula 301",
        capacidad=40,
        ubicacion="Edificio A",
    )
    async_db_session.add(c)
    await async_db_session.commit()
    await async_db_session.refresh(c)
    return c


@pytest.fixture
async def async_subject(async_db_session, async_profesor_user):
    """Materia para tests async de schedules."""
    s = Subject(
        nombre="Matemáticas Avanzadas",
        codigo_institucional="MAT301",
        numero_creditos=3,
        profesor_id=async_profesor_user.id,
    )
    async_db_session.add(s)
    await async_db_session.commit()
    await async_db_session.refresh(s)
    return s


@pytest.fixture
async def async_estudiante_user(async_db_session):
    """Estudiante para tests async de schedules."""
    u = User(
        email="estudiante@test.com",
        password_hash=hashpw(b"password123", gensalt()).decode(),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante",
        apellido="Test",
        codigo_institucional="EST001",
        fecha_nacimiento=date(2005, 3, 20),
    )
    async_db_session.add(u)
    await async_db_session.commit()
    await async_db_session.refresh(u)
    return u


@pytest.fixture
async def async_enrollment(async_db_session, async_estudiante_user, async_subject):
    """Inscripción para tests async de schedules."""
    e = Enrollment(
        estudiante_id=async_estudiante_user.id,
        subject_id=async_subject.id,
    )
    async_db_session.add(e)
    await async_db_session.commit()
    await async_db_session.refresh(e)
    return e


@pytest.fixture
async def async_classroom2(async_db_session):
    """Segunda aula para tests async de solapamiento."""
    c = Classroom(codigo="AULA-302", nombre="Aula 302", capacidad=30)
    async_db_session.add(c)
    await async_db_session.commit()
    await async_db_session.refresh(c)
    return c


@pytest.fixture
async def async_subject2(async_db_session, async_profesor_user):
    """Segunda materia (mismo profesor) para tests async."""
    s = Subject(
        nombre="Física",
        codigo_institucional="FIS301",
        numero_creditos=3,
        profesor_id=async_profesor_user.id,
    )
    async_db_session.add(s)
    await async_db_session.commit()
    await async_db_session.refresh(s)
    return s


@pytest.fixture
async def async_enrollment2(async_db_session, async_estudiante_user, async_subject2):
    """Inscripción en segunda materia para tests async."""
    e = Enrollment(
        estudiante_id=async_estudiante_user.id,
        subject_id=async_subject2.id,
    )
    async_db_session.add(e)
    await async_db_session.commit()
    await async_db_session.refresh(e)
    return e


# ===== ASYNC FIXTURES FOR ATTENDANCE TESTS =====
@pytest.fixture
async def async_clase_session(async_db_session, async_subject, async_profesor_user):
    """Clase session para tests async de attendance."""
    today = date.today()
    clase = ClaseSession(
        subject_id=async_subject.id,
        fecha=today,
        hora_inicio=datetime.combine(today, datetime.min.time().replace(hour=8)),
        hora_fin=datetime.combine(today, datetime.min.time().replace(hour=10)),
        descripcion="Clase de prueba async",
        creado_por=async_profesor_user.id,
    )
    async_db_session.add(clase)
    await async_db_session.commit()
    await async_db_session.refresh(clase)
    return clase


# ===== HTTP CLIENT FIXTURE =====
@pytest.fixture
async def client():
    """Create an async HTTP client for integration tests."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
