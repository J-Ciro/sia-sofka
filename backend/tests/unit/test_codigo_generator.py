"""Unit tests for codigo_generator utility."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.utils.codigo_generator import (
    generar_codigo_institucional,
    generar_codigo_institucional_sync,
    generar_codigo_materia,
    generar_codigo_materia_sync,
)
from app.core.security import get_password_hash


# ==================== Tests for generar_codigo_institucional (async) ====================

@pytest.mark.asyncio
async def test_generar_codigo_institucional_estudiante(async_db_session: AsyncSession):
    """Test generating code for Estudiante role."""
    codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
    assert codigo.startswith("EST-")
    assert len(codigo.split("-")) == 3
    year = codigo.split("-")[1]
    assert year == str(date.today().year)


@pytest.mark.asyncio
async def test_generar_codigo_institucional_profesor(async_db_session: AsyncSession):
    """Test generating code for Profesor role."""
    codigo = await generar_codigo_institucional(async_db_session, "Profesor")
    assert codigo.startswith("PROF-")
    assert len(codigo.split("-")) == 3


@pytest.mark.asyncio
async def test_generar_codigo_institucional_admin(async_db_session: AsyncSession):
    """Test generating code for Admin role."""
    codigo = await generar_codigo_institucional(async_db_session, "Admin")
    assert codigo.startswith("ADM-")
    assert len(codigo.split("-")) == 3


@pytest.mark.asyncio
async def test_generar_codigo_institucional_unknown_role(async_db_session: AsyncSession):
    """Test generating code for unknown role (should use USR prefix)."""
    codigo = await generar_codigo_institucional(async_db_session, "UnknownRole")
    assert codigo.startswith("USR-")
    assert len(codigo.split("-")) == 3


@pytest.mark.asyncio
async def test_generar_codigo_institucional_sequential(async_db_session: AsyncSession):
    """Test that codes are generated sequentially."""
    codigo1 = await generar_codigo_institucional(async_db_session, "Estudiante")
    
    # Create a user with the first code
    user = User(
        email="test1@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Test",
        apellido="User",
        codigo_institucional=codigo1,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    
    # Generate another code - should be sequential
    codigo2 = await generar_codigo_institucional(async_db_session, "Estudiante")
    assert codigo1 != codigo2
    
    # Extract sequential numbers
    seq1 = int(codigo1.split("-")[2])
    seq2 = int(codigo2.split("-")[2])
    assert seq2 == seq1 + 1


@pytest.mark.asyncio
async def test_generar_codigo_institucional_handles_duplicates(async_db_session: AsyncSession):
    """Test that code generator handles duplicate codes by incrementing."""
    # Generate first code
    codigo1 = await generar_codigo_institucional(async_db_session, "Estudiante")
    
    # Manually create a user with a code that would be generated next
    # This simulates a race condition
    user1 = User(
        email="test1@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Test",
        apellido="User1",
        codigo_institucional=codigo1,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(user1)
    await async_db_session.commit()
    
    # Generate another code - should skip the duplicate
    codigo2 = await generar_codigo_institucional(async_db_session, "Estudiante")
    assert codigo1 != codigo2
    
    # Create user with second code
    user2 = User(
        email="test2@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Test",
        apellido="User2",
        codigo_institucional=codigo2,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(user2)
    await async_db_session.commit()
    
    # Generate third code - should continue sequence
    codigo3 = await generar_codigo_institucional(async_db_session, "Estudiante")
    assert codigo3 not in [codigo1, codigo2]


# ==================== Tests for generar_codigo_institucional_sync ====================

def test_generar_codigo_institucional_sync_estudiante(db_session: Session):
    """Test generating code for Estudiante role (sync version)."""
    codigo = generar_codigo_institucional_sync(db_session, "Estudiante")
    assert codigo.startswith("EST-")
    assert len(codigo.split("-")) == 3


def test_generar_codigo_institucional_sync_unknown_role(db_session: Session):
    """Test generating code for unknown role (sync version)."""
    codigo = generar_codigo_institucional_sync(db_session, "UnknownRole")
    assert codigo.startswith("USR-")


def test_generar_codigo_institucional_sync_sequential(db_session: Session):
    """Test that codes are generated sequentially (sync version)."""
    codigo1 = generar_codigo_institucional_sync(db_session, "Estudiante")
    
    user = User(
        email="test1@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Test",
        apellido="User",
        codigo_institucional=codigo1,
        fecha_nacimiento=date(2000, 1, 1),
    )
    db_session.add(user)
    db_session.commit()
    
    codigo2 = generar_codigo_institucional_sync(db_session, "Estudiante")
    assert codigo1 != codigo2


# ==================== Tests for generar_codigo_materia (async) ====================

@pytest.mark.asyncio
async def test_generar_codigo_materia_basic(async_db_session: AsyncSession):
    """Test generating code for a subject with a simple name."""
    codigo = await generar_codigo_materia(async_db_session, "Matemáticas")
    # Takes first 4 letters if >= 4, so "MATE"
    assert codigo.startswith("MATE-") or codigo.startswith("MAT-")
    assert len(codigo.split("-")) == 2
    assert codigo.split("-")[1].isdigit()


@pytest.mark.asyncio
async def test_generar_codigo_materia_with_ignored_words(async_db_session: AsyncSession):
    """Test that common words are ignored when generating prefix."""
    codigo = await generar_codigo_materia(async_db_session, "de la Física")
    # "Física" -> first 4 letters = "FISI" or first 3 = "FIS"
    assert codigo.startswith("FISI-") or codigo.startswith("FIS-")


@pytest.mark.asyncio
async def test_generar_codigo_materia_short_name(async_db_session: AsyncSession):
    """Test generating code for a subject with a short name."""
    codigo = await generar_codigo_materia(async_db_session, "IA")
    # Should pad with X to make 3 characters
    assert len(codigo.split("-")[0]) >= 3


@pytest.mark.asyncio
async def test_generar_codigo_materia_only_ignored_words(async_db_session: AsyncSession):
    """Test generating code when all words are ignored."""
    codigo = await generar_codigo_materia(async_db_session, "de la y el")
    # The code should still generate a valid prefix (may use first word or default)
    assert len(codigo.split("-")) == 2
    assert codigo.split("-")[1].isdigit()


@pytest.mark.asyncio
async def test_generar_codigo_materia_special_characters(async_db_session: AsyncSession):
    """Test that special characters are removed from prefix."""
    codigo = await generar_codigo_materia(async_db_session, "Cálculo 101")
    # Should remove numbers and keep only letters
    prefix = codigo.split("-")[0]
    assert prefix.isalpha()


@pytest.mark.asyncio
async def test_generar_codigo_materia_sequential(async_db_session: AsyncSession):
    """Test that subject codes are generated sequentially."""
    codigo1 = await generar_codigo_materia(async_db_session, "Matemáticas")
    
    # Create profesor first
    codigo_prof = await generar_codigo_institucional(async_db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(profesor)
    await async_db_session.commit()
    await async_db_session.refresh(profesor)
    
    # Create a subject with the first code
    subject1 = Subject(
        nombre="Matemáticas",
        codigo_institucional=codigo1,
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    async_db_session.add(subject1)
    await async_db_session.commit()
    
    # Generate another code with same prefix - should be sequential
    codigo2 = await generar_codigo_materia(async_db_session, "Matemáticas Avanzadas")
    assert codigo1 != codigo2
    
    # Extract sequential numbers
    seq1 = int(codigo1.split("-")[1])
    seq2 = int(codigo2.split("-")[1])
    assert seq2 == seq1 + 1


@pytest.mark.asyncio
async def test_generar_codigo_materia_different_prefixes(async_db_session: AsyncSession):
    """Test that different subject names generate different prefixes."""
    codigo1 = await generar_codigo_materia(async_db_session, "Matemáticas")
    codigo2 = await generar_codigo_materia(async_db_session, "Física")
    
    prefix1 = codigo1.split("-")[0]
    prefix2 = codigo2.split("-")[0]
    assert prefix1 != prefix2


# ==================== Tests for generar_codigo_materia_sync ====================

def test_generar_codigo_materia_sync_basic(db_session: Session):
    """Test generating code for a subject (sync version)."""
    codigo = generar_codigo_materia_sync(db_session, "Matemáticas")
    # Takes first 4 letters if >= 4, so "MATE"
    assert codigo.startswith("MATE-") or codigo.startswith("MAT-")
    assert len(codigo.split("-")) == 2


def test_generar_codigo_materia_sync_with_ignored_words(db_session: Session):
    """Test that common words are ignored (sync version)."""
    codigo = generar_codigo_materia_sync(db_session, "de la Física")
    # "Física" -> first 4 letters = "FISI" or first 3 = "FIS"
    assert codigo.startswith("FISI-") or codigo.startswith("FIS-")


def test_generar_codigo_materia_sync_only_ignored_words(db_session: Session):
    """Test generating code when all words are ignored (sync version)."""
    codigo = generar_codigo_materia_sync(db_session, "de la y el")
    # The code should still generate a valid prefix
    assert len(codigo.split("-")) == 2
    assert codigo.split("-")[1].isdigit()


def test_generar_codigo_materia_sync_sequential(db_session: Session):
    """Test that codes are generated sequentially (sync version)."""
    codigo1 = generar_codigo_materia_sync(db_session, "Matemáticas")
    
    # Create profesor first
    codigo_prof = generar_codigo_institucional_sync(db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor)
    db_session.commit()
    db_session.refresh(profesor)
    
    subject1 = Subject(
        nombre="Matemáticas",
        codigo_institucional=codigo1,
        numero_creditos=3,
        profesor_id=profesor.id,
    )
    db_session.add(subject1)
    db_session.commit()
    
    codigo2 = generar_codigo_materia_sync(db_session, "Matemáticas Avanzadas")
    assert codigo1 != codigo2
