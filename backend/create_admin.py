"""Script para crear un usuario administrador inicial."""

import asyncio
import sys
from app.core.database import AsyncSessionLocal, Base, get_engine
from app.models.user import User, UserRole
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash
from datetime import date


async def create_admin():
    """Crear usuario administrador inicial."""
    # Obtener engine
    engine = get_engine()
    
    # Crear tablas si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        # Verificar si ya existe un admin
        from app.repositories.user_repository import UserRepository
        repo = UserRepository(session)
        existing_admin = await repo.get_by_email("admin@sofka.edu.co")
        
        if existing_admin:
            print("✓ Ya existe un administrador con el email admin@sofka.edu.co")
            print(f"  Código: {existing_admin.codigo_institucional}")
            return
        
        # Crear admin
        codigo = await generar_codigo_institucional(session, "Admin")
        admin = User(
            email="admin@sofka.edu.co",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            nombre="Administrador",
            apellido="Sistema",
            codigo_institucional=codigo,
            fecha_nacimiento=date(1980, 1, 1),
        )
        session.add(admin)
        await session.commit()
        await session.refresh(admin)
        
        print("=" * 60)
        print("✓ ADMINISTRADOR CREADO EXITOSAMENTE")
        print("=" * 60)
        print(f"Email: {admin.email}")
        print(f"Password: admin123")
        print(f"Código Institucional: {admin.codigo_institucional}")
        print()
        print("⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(create_admin())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

