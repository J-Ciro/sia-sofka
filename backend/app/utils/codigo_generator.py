"""Utility for generating institutional codes."""

from datetime import datetime
from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.models.user import User
from app.models.subject import Subject


def generar_codigo_institucional_sync(
    db: Session, role: str
) -> str:
    """Generate institutional code for a user based on role (synchronous version).
    
    Args:
        db: Synchronous database session
        role: User role (Estudiante, Profesor, Admin)
    
    Returns:
        Generated institutional code in format: {PREFIX}-{YEAR}-{SEQUENTIAL}
    """
    prefixes = {
        "Estudiante": "EST",
        "Profesor": "PROF",
        "Admin": "ADM",
    }
    
    prefix = prefixes.get(role, "USR")
    current_year = datetime.now().year
    
    # Get the count of users with the same role and year
    stmt = select(func.count(User.id)).where(
        User.role == role,
        User.codigo_institucional.like(f"{prefix}-{current_year}-%")
    )
    result = db.execute(stmt)
    count = result.scalar() or 0
    
    # Generate sequential number with 4 digits
    sequential = str(count + 1).zfill(4)
    
    return f"{prefix}-{current_year}-{sequential}"


async def generar_codigo_institucional(
    db: AsyncSession, role: str
) -> str:
    """Generate institutional code for a user based on role (async version).
    
    Args:
        db: Async database session
        role: User role (Estudiante, Profesor, Admin)
    
    Returns:
        Generated institutional code in format: {PREFIX}-{YEAR}-{SEQUENTIAL}
    """
    prefixes = {
        "Estudiante": "EST",
        "Profesor": "PROF",
        "Admin": "ADM",
    }
    
    prefix = prefixes.get(role, "USR")
    current_year = datetime.now().year
    
    # Get the count of users with the same role and year
    stmt = select(func.count(User.id)).where(
        User.role == role,
        User.codigo_institucional.like(f"{prefix}-{current_year}-%")
    )
    result = await db.execute(stmt)
    count = result.scalar() or 0
    
    # Generate sequential number with 4 digits
    sequential = str(count + 1).zfill(4)
    
    return f"{prefix}-{current_year}-{sequential}"


def generar_codigo_materia_sync(
    db: Session, nombre_materia: str
) -> str:
    """Generate institutional code for a subject based on name (synchronous version).
    
    Args:
        db: Synchronous database session
        nombre_materia: Subject name
    
    Returns:
        Generated institutional code in format: {PREFIX}-{SEQUENTIAL}
        where PREFIX is the first 3-4 letters of the subject name (uppercase)
    """
    # Generate prefix from first letters of subject name
    # Remove common words and get first meaningful word
    palabras_ignorar = {"de", "la", "el", "y", "en", "con", "para", "por"}
    palabras = nombre_materia.upper().split()
    palabras_importantes = [p for p in palabras if p not in palabras_ignorar]
    
    if palabras_importantes:
        primera_palabra = palabras_importantes[0]
        # Take first 3-4 letters, max 4
        prefix = primera_palabra[:4] if len(primera_palabra) >= 4 else primera_palabra.ljust(3, 'X')[:3]
        # Remove special characters, keep only letters
        prefix = ''.join(c for c in prefix if c.isalpha())
        if len(prefix) < 3:
            prefix = (prefix + 'XXX')[:3]
    else:
        prefix = "MAT"
    
    # Get the count of subjects with the same prefix
    stmt = select(func.count(Subject.id)).where(
        Subject.codigo_institucional.like(f"{prefix}-%")
    )
    result = db.execute(stmt)
    count = result.scalar() or 0
    
    # Generate sequential number with 3 digits
    sequential = str(count + 1).zfill(3)
    
    return f"{prefix}-{sequential}"


async def generar_codigo_materia(
    db: AsyncSession, nombre_materia: str
) -> str:
    """Generate institutional code for a subject based on name (async version).
    
    Args:
        db: Async database session
        nombre_materia: Subject name
    
    Returns:
        Generated institutional code in format: {PREFIX}-{SEQUENTIAL}
        where PREFIX is the first 3-4 letters of the subject name (uppercase)
    """
    # Generate prefix from first letters of subject name
    # Remove common words and get first meaningful word
    palabras_ignorar = {"de", "la", "el", "y", "en", "con", "para", "por"}
    palabras = nombre_materia.upper().split()
    palabras_importantes = [p for p in palabras if p not in palabras_ignorar]
    
    if palabras_importantes:
        primera_palabra = palabras_importantes[0]
        # Take first 3-4 letters, max 4
        prefix = primera_palabra[:4] if len(primera_palabra) >= 4 else primera_palabra.ljust(3, 'X')[:3]
        # Remove special characters, keep only letters
        prefix = ''.join(c for c in prefix if c.isalpha())
        if len(prefix) < 3:
            prefix = (prefix + 'XXX')[:3]
    else:
        prefix = "MAT"
    
    # Get the count of subjects with the same prefix
    stmt = select(func.count(Subject.id)).where(
        Subject.codigo_institucional.like(f"{prefix}-%")
    )
    result = await db.execute(stmt)
    count = result.scalar() or 0
    
    # Generate sequential number with 3 digits
    sequential = str(count + 1).zfill(3)
    
    return f"{prefix}-{sequential}"
