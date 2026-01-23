"""Script para crear usuarios de test para E2E tests."""

import asyncio
import sys
from app.core.database import AsyncSessionLocal, Base, get_engine
from app.models.user import User, UserRole
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash
from datetime import date


async def create_test_users():
    """Crear usuarios de test para E2E tests."""
    # Obtener engine
    engine = get_engine()
    
    # Crear tablas si no existen
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSessionLocal() as session:
        from app.repositories.user_repository import UserRepository
        repo = UserRepository(session)
        
        # Usuarios de test a crear
        test_users = [
            {
                "email": "juan@mail.com",
                "password": "juan123",
                "role": UserRole.PROFESOR,
                "nombre": "Juan",
                "apellido": "Pérez",
                "fecha_nacimiento": date(1985, 5, 15),
                "area_ensenanza": "Matemáticas",
            },
            {
                "email": "sara@mail.com",
                "password": "sara123",
                "role": UserRole.ESTUDIANTE,
                "nombre": "Sara",
                "apellido": "García",
                "fecha_nacimiento": date(2000, 3, 20),
                "programa_academico": "Ingeniería de Sistemas",
                "ciudad_residencia": "Bogotá",
                "numero_contacto": "3001234567",
            },
        ]
        
        created_count = 0
        existing_count = 0
        
        for user_data in test_users:
            # Verificar si ya existe
            existing_user = await repo.get_by_email(user_data["email"])
            
            if existing_user:
                print(f"✓ Ya existe usuario: {user_data['email']} ({user_data['role'].value})")
                existing_count += 1
                continue
            
            # Generar código institucional
            codigo = await generar_codigo_institucional(session, user_data["role"].value)
            
            # Crear usuario
            user = User(
                email=user_data["email"],
                password_hash=get_password_hash(user_data["password"]),
                role=user_data["role"],
                nombre=user_data["nombre"],
                apellido=user_data["apellido"],
                codigo_institucional=codigo,
                fecha_nacimiento=user_data["fecha_nacimiento"],
                numero_contacto=user_data.get("numero_contacto"),
                programa_academico=user_data.get("programa_academico"),
                ciudad_residencia=user_data.get("ciudad_residencia"),
                area_ensenanza=user_data.get("area_ensenanza"),
            )
            
            session.add(user)
            created_count += 1
            print(f"✓ Creado usuario: {user_data['email']} ({user_data['role'].value})")
        
        await session.commit()
        
        print("=" * 60)
        print(f"✓ USUARIOS DE TEST CREADOS")
        print("=" * 60)
        print(f"Creados: {created_count}")
        print(f"Existentes: {existing_count}")
        print()
        print("Usuarios disponibles para tests:")
        for user_data in test_users:
            print(f"  - {user_data['email']} ({user_data['role'].value}) - Password: {user_data['password']}")
        print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(create_test_users())
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
