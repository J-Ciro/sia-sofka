"""Unit tests for SubjectSerializer."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.api.v1.serializers.subject_serializer import SubjectSerializer
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.fixture
async def test_data_subject_serializer(async_db_session: AsyncSession):
    """Create test data for subject serializer tests."""
    import uuid
    # Use UUID to ensure unique codes
    unique_id = str(uuid.uuid4())[:8]
    
    # Profesores - Use unique codes directly
    codigo_prof1 = f"PROF-TEST-{unique_id}-1"
    profesor1 = User(
        email=f"profesor1-{unique_id}@subject-serializer.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Pedro",
        apellido="Martínez",
        codigo_institucional=codigo_prof1,
        fecha_nacimiento=date(1980, 1, 1),
    )
    
    codigo_prof2 = f"PROF-TEST-{unique_id}-2"
    profesor2 = User(
        email=f"profesor2-{unique_id}@subject-serializer.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Laura",
        apellido="Sánchez",
        codigo_institucional=codigo_prof2,
        fecha_nacimiento=date(1985, 1, 1),
    )
    
    async_db_session.add(profesor1)
    async_db_session.add(profesor2)
    await async_db_session.commit()
    await async_db_session.refresh(profesor1)
    await async_db_session.refresh(profesor2)
    
    # Subjects
    subject1 = Subject(
        nombre="Biología",
        codigo_institucional=f"BIO-TEST-{unique_id}-101",
        numero_creditos=4,
        horario="Lunes 8:00-10:00",
        descripcion="Curso de biología",
        profesor_id=profesor1.id,
    )
    subject2 = Subject(
        nombre="Historia",
        codigo_institucional=f"HIS-TEST-{unique_id}-101",
        numero_creditos=2,
        horario="Viernes 14:00-16:00",
        descripcion="Curso de historia",
        profesor_id=profesor2.id,
    )
    # Create a third profesor for subject3 (since profesor_id cannot be NULL)
    codigo_prof3 = f"PROF-TEST-{unique_id}-3"
    profesor3 = User(
        email=f"profesor3-{unique_id}@subject-serializer.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Carlos",
        apellido="González",
        codigo_institucional=codigo_prof3,
        fecha_nacimiento=date(1990, 1, 1),
    )
    async_db_session.add(profesor3)
    await async_db_session.commit()
    await async_db_session.refresh(profesor3)
    
    subject3 = Subject(
        nombre="Arte",
        codigo_institucional=f"ART-TEST-{unique_id}-101",
        numero_creditos=2,
        horario="Jueves 10:00-12:00",
        descripcion="Curso de arte",
        profesor_id=profesor3.id,  # Assign profesor3
    )
    
    async_db_session.add(subject1)
    async_db_session.add(subject2)
    async_db_session.add(subject3)
    await async_db_session.commit()
    await async_db_session.refresh(subject1)
    await async_db_session.refresh(subject2)
    await async_db_session.refresh(subject3)
    
    # Manually set relationships for testing
    subject1.profesor = profesor1
    subject2.profesor = profesor2
    subject3.profesor = profesor3
    
    return {
        "profesores": [profesor1, profesor2, profesor3],
        "subjects": [subject1, subject2, subject3],
    }


def test_serialize_batch_empty_list():
    """Test serializing empty list."""
    result = SubjectSerializer.serialize_batch([])
    assert result == []


@pytest.mark.asyncio
async def test_serialize_batch_with_profesor(
    test_data_subject_serializer
):
    """Test serializing subjects with profesor relationship."""
    subjects = test_data_subject_serializer["subjects"]
    
    result = SubjectSerializer.serialize_batch(subjects)
    
    assert len(result) == 3
    assert result[0].nombre == "Biología"
    assert result[0].profesor is not None
    assert result[0].profesor.nombre == "Pedro"
    assert result[0].profesor.apellido == "Martínez"
    
    assert result[1].nombre == "Historia"
    assert result[1].profesor is not None
    assert result[1].profesor.nombre == "Laura"
    
    assert result[2].nombre == "Arte"
    assert result[2].profesor is not None  # Has profesor assigned
    assert result[2].profesor.nombre == "Carlos"


@pytest.mark.asyncio
async def test_serialize_batch_all_fields(
    test_data_subject_serializer
):
    """Test that all fields are serialized correctly."""
    data = test_data_subject_serializer
    subjects = data["subjects"]
    
    result = SubjectSerializer.serialize_batch(subjects)
    
    subject = result[0]
    original_subject = subjects[0]
    assert subject.id is not None
    assert subject.id == original_subject.id
    assert subject.nombre == "Biología"
    assert subject.codigo_institucional == original_subject.codigo_institucional
    assert subject.codigo_institucional.startswith("BIO-TEST-")
    assert subject.numero_creditos == 4
    assert subject.horario == "Lunes 8:00-10:00"
    assert subject.descripcion == "Curso de biología"
    assert subject.profesor_id is not None
    assert subject.profesor_id == original_subject.profesor_id


@pytest.mark.asyncio
async def test_serialize_batch_without_profesor_loaded(
    test_data_subject_serializer
):
    """Test serializing when profesor relationship is not loaded."""
    subjects = test_data_subject_serializer["subjects"]
    
    # Remove profesor relationship (simulating lazy loading not executed)
    subjects[0].profesor = None
    
    result = SubjectSerializer.serialize_batch(subjects)
    
    assert len(result) == 3
    assert result[0].profesor is None  # Profesor relationship not loaded
    assert result[1].profesor is not None  # Still has profesor
    assert result[2].profesor is not None  # Still has profesor

