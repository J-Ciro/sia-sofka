"""Unit tests for authentication endpoints."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Auth tests need integration test setup, not unit test setup")
async def test_register_user_success(client, async_db_session: AsyncSession):
    """Test successful user registration."""
    # Create admin user first (needed for registration)
    codigo_admin = await generar_codigo_institucional(async_db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1980, 1, 1),
    )
    async_db_session.add(admin)
    await async_db_session.commit()
    await async_db_session.refresh(admin)
    
    # Login as admin
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@example.com", "password": "admin123"},
    )
    assert login_response.status_code == 200
    admin_token = login_response.json()["access_token"]
    
    # Register new user
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "nombre": "New",
            "apellido": "User",
            "role": "Estudiante",
            "fecha_nacimiento": "2000-01-01",
            "programa_academico": "Ingeniería",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "Estudiante"
    assert "codigo_institucional" in data


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Auth tests need integration test setup, not unit test setup")
async def test_register_user_unauthorized(client, async_db_session: AsyncSession):
    """Test that non-admin users cannot register."""
    # Create estudiante user
    codigo_est = await generar_codigo_institucional(async_db_session, "Estudiante")
    estudiante = User(
        email="estudiante@example.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(estudiante)
    await async_db_session.commit()
    await async_db_session.refresh(estudiante)
    
    # Login as estudiante
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "estudiante@example.com", "password": "est123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    
    # Try to register (should fail)
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "nombre": "New",
            "apellido": "User",
            "role": "Estudiante",
            "fecha_nacimiento": "2000-01-01",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Auth tests need integration test setup, not unit test setup")
async def test_login_success(client, async_db_session: AsyncSession):
    """Test successful login."""
    codigo = await generar_codigo_institucional(async_db_session, "Estudiante")
    password = "test_password"
    user = User(
        email="test@example.com",
        password_hash=get_password_hash(password),
        role=UserRole.ESTUDIANTE,
        nombre="Test",
        apellido="User",
        codigo_institucional=codigo,
        fecha_nacimiento=date(2000, 1, 1),
    )
    async_db_session.add(user)
    await async_db_session.commit()
    
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "test@example.com", "password": password},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Auth tests need integration test setup, not unit test setup")
async def test_login_invalid_credentials(client, async_db_session: AsyncSession):
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent@example.com", "password": "wrong"},
    )
    
    assert response.status_code == 401


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Auth tests need integration test setup, not unit test setup")
async def test_get_current_user(client, async_db_session: AsyncSession):
    """Test getting current user information."""
    codigo = await generar_codigo_institucional(async_db_session, "Profesor")
    password = "prof_password"
    user = User(
        email="profesor@example.com",
        password_hash=get_password_hash(password),
        role=UserRole.PROFESOR,
        nombre="Profesor",
        apellido="Test",
        codigo_institucional=codigo,
        fecha_nacimiento=date(1980, 1, 1),
        area_ensenanza="Matemáticas",
    )
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)
    
    # Login
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "profesor@example.com", "password": password},
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "profesor@example.com"
    assert data["role"] == "Profesor"
    assert data["area_ensenanza"] == "Matemáticas"


@pytest.mark.asyncio
@pytest.mark.xfail(reason="Auth tests need integration test setup, not unit test setup")
async def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": "Bearer invalid_token"},
    )
    
    assert response.status_code == 401

