# SIA SOFKA U - Sistema de Información Académica

[![CI Pipeline](https://github.com/YOUR_USERNAME/sia-sofka/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/sia-sofka/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18.3.1-blue.svg)](https://reactjs.org/)
[![Coverage](https://img.shields.io/badge/coverage-87%25+-green.svg)](https://github.com/YOUR_USERNAME/sia-sofka)

Sistema de Información Académica SOFKA U es una aplicación full-stack diseñada para gestionar la información académica de una institución educativa. El sistema permite a administradores, profesores y estudiantes gestionar usuarios, materias, inscripciones y calificaciones, con capacidades avanzadas de generación de reportes en múltiples formatos.

---

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Arquitectura](#-arquitectura)
- [Stack Tecnológico](#-stack-tecnológico)
- [Patrones de Diseño](#-patrones-de-diseño)
- [Factory Pattern - Generación de Reportes](#-factory-pattern---generación-de-reportes)
- [Instalación y Configuración](#-instalación-y-configuración)
- [Ejecución del Proyecto](#-ejecución-del-proyecto)
- [Testing](#-testing)
- [CI/CD Pipeline](#-cicd-pipeline)
- [AI Collaboration Log](#-ai-collaboration-log)

---

## 🎯 Descripción del Proyecto

SIA SOFKA U es un sistema completo de gestión académica que permite:

- **Gestión de Usuarios**: Administradores pueden crear y gestionar estudiantes y profesores
- **Gestión de Materias**: Administración completa del catálogo de materias con asignación de profesores
- **Inscripciones**: Sistema de inscripción de estudiantes a materias
- **Calificaciones**: Profesores y administradores pueden registrar y gestionar notas de estudiantes
- **Reportes**: Generación de reportes académicos en formatos PDF, HTML y JSON
- **Roles y Permisos**: Sistema robusto de autenticación y autorización basado en roles (Admin, Profesor, Estudiante)

El sistema está diseñado siguiendo principios de **Clean Code**, **SOLID**, **TDD** y **patrones de diseño** para garantizar escalabilidad, mantenibilidad y calidad del código.

---

## 🏗️ Arquitectura

El proyecto sigue una **arquitectura en capas** (Layered Architecture) con separación clara de responsabilidades:

### Backend (FastAPI)

```
backend/
├── app/
│   ├── api/                    # Capa de Presentación (Endpoints HTTP)
│   │   └── v1/
│   │       ├── endpoints/      # Endpoints REST por recurso
│   │       ├── serializers/    # Serialización de datos
│   │       └── validators/     # Validación de permisos y datos
│   │
│   ├── services/               # Capa de Lógica de Negocio
│   │   ├── admin_service.py
│   │   ├── profesor_service.py
│   │   ├── estudiante_service.py
│   │   ├── user_service.py
│   │   ├── subject_service.py
│   │   ├── enrollment_service.py
│   │   └── grade_service.py
│   │
│   ├── repositories/           # Capa de Acceso a Datos
│   │   ├── base.py            # Repositorio abstracto
│   │   ├── mixins.py          # Mixins reutilizables (EagerLoad, Pagination)
│   │   ├── protocols.py       # Interfaces/Protocols para DIP
│   │   ├── user_repository.py
│   │   ├── subject_repository.py
│   │   ├── enrollment_repository.py
│   │   └── grade_repository.py
│   │
│   ├── models/                 # Capa de Modelos (ORM)
│   │   ├── user.py
│   │   ├── subject.py
│   │   ├── enrollment.py
│   │   └── grade.py
│   │
│   ├── schemas/                # Capa de Validación (Pydantic)
│   │   ├── user.py
│   │   ├── subject.py
│   │   ├── enrollment.py
│   │   ├── grade.py
│   │   └── report.py
│   │
│   ├── factories/              # Patrones de Diseño
│   │   ├── report_factory.py   # Factory Method + Registry Pattern
│   │   ├── pdf_generator.py
│   │   ├── html_generator.py
│   │   └── json_generator.py
│   │
│   ├── core/                   # Configuración y Utilidades Core
│   │   ├── config.py          # Configuración centralizada
│   │   ├── database.py        # Configuración de BD
│   │   ├── security.py        # JWT, bcrypt
│   │   ├── exceptions.py      # Excepciones personalizadas
│   │   ├── decorators.py      # Decoradores cross-cutting
│   │   ├── sanitizers.py      # Sanitización de inputs
│   │   └── logging.py         # Sistema de logging
│   │
│   └── utils/                  # Utilidades
│       └── codigo_generator.py
│
└── tests/                      # Tests (Unitarios e Integración)
    ├── unit/
    └── integration/
```

### Frontend (React)

```
frontend/
├── src/
│   ├── components/             # Componentes React
│   │   ├── auth/              # Componentes de autenticación
│   │   ├── layout/            # Layout y Sidebar
│   │   ├── dashboard/         # Páginas del dashboard
│   │   ├── modals/            # Modales de creación/edición
│   │   └── common/            # Componentes reutilizables
│   │
│   ├── services/               # Servicios API
│   │   ├── api.js             # Cliente axios configurado
│   │   └── apiService.js      # Servicios por entidad
│   │
│   ├── context/                # Context API (Estado global)
│   │   └── AuthContext.jsx
│   │
│   └── config/                 # Configuración
│       └── constants.js
│
```

### E2E (Playwright)

```
e2e/                            # Tests E2E (fuera de frontend/ y backend/)
├── playwright.config.js
├── package.json
├── tests/
│   ├── e2e/                    # Specs: auth, users, subjects, grades, enrollments, navigation
│   └── fixtures/
│       └── auth.js
├── install-playwright.ps1
└── PLAYWRIGHT_GUIDE.md
```

### Flujo de Datos

```
Cliente (React) 
    ↓ HTTP Request
API Endpoints (FastAPI)
    ↓ Validación y Serialización
Services (Lógica de Negocio)
    ↓ Operaciones de Negocio
Repositories (Acceso a Datos)
    ↓ Queries SQLAlchemy
Database (PostgreSQL)
```

---

## 🛠️ Stack Tecnológico

### Backend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **Python** | 3.11+ | Lenguaje principal |
| **FastAPI** | 0.104.1 | Framework web asíncrono |
| **SQLAlchemy** | 2.0.23 | ORM asíncrono |
| **PostgreSQL** | 15 | Base de datos relacional |
| **Pydantic** | 2.5.0 | Validación de datos y schemas |
| **JWT** (python-jose) | 3.3.0 | Autenticación |
| **bcrypt** | - | Hashing de contraseñas |
| **ReportLab** | 4.0.7 | Generación de PDFs |
| **Jinja2** | 3.1.2 | Templates HTML |
| **pytest** | - | Framework de testing |
| **pytest-asyncio** | - | Testing asíncrono |
| **pytest-cov** | - | Coverage de tests |

### Frontend

| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **React** | 18.3.1 | Biblioteca de UI |
| **Vite** | 5.4.2 | Build tool y dev server |
| **React Router** | 6.20.0 | Enrutamiento |
| **Axios** | 1.6.2 | Cliente HTTP |
| **Tailwind CSS** | 3.4.1 | Framework CSS |
| **Lucide React** | 0.263.1 | Iconos |
| **Playwright** | 1.57.0 | Testing E2E |

### DevOps y Herramientas

| Herramienta | Propósito |
|-------------|-----------|
| **Docker** | Containerización |
| **Docker Compose** | Orquestación de servicios |
| **GitHub Actions** | CI/CD Pipeline |
| **Black** | Formateo de código Python |
| **flake8** | Linting Python |
| **mypy** | Type checking |
| **isort** | Ordenamiento de imports |
| **pre-commit** | Git hooks |

---

## 🎨 Patrones de Diseño

El proyecto implementa varios patrones de diseño siguiendo principios SOLID:

### 1. **Repository Pattern**
Separa la lógica de acceso a datos de la lógica de negocio. Todos los repositorios heredan de `AbstractRepository` y pueden usar mixins para funcionalidad adicional.

```python
# Ejemplo: GradeRepository
class GradeRepository(AbstractRepository[Grade], EagerLoadMixin, PaginationMixin):
    async def get_many_with_relations(self, ...):
        # Implementación con eager loading
```

### 2. **Factory Method Pattern** ⭐
Implementado para la generación de reportes. Permite crear diferentes tipos de generadores (PDF, HTML, JSON) sin acoplar el código cliente a clases concretas.

### 3. **Registry Pattern**
Combinado con Factory Method para registrar dinámicamente nuevos formatos de reporte sin modificar código existente.

### 4. **Singleton Pattern**
Los generadores de reportes se reutilizan como instancias singleton para optimizar recursos.

### 5. **Dependency Injection**
FastAPI proporciona DI nativa a través de `Depends()`. Los servicios reciben repositorios como dependencias.

### 6. **Strategy Pattern**
Diferentes estrategias de generación de reportes (PDF, HTML, JSON) implementan la misma interfaz.

### 7. **Mixin Pattern**
Mixins reutilizables (`EagerLoadMixin`, `PaginationMixin`, `TimestampMixin`) para compartir funcionalidad entre repositorios.

### 8. **Decorator Pattern**
Decoradores cross-cutting para manejo de errores, logging, retry, y validación.

---

## 🏭 Factory Pattern - Generación de Reportes

El sistema implementa un **Factory Method** combinado con **Registry Pattern** para la generación de reportes académicos. Esta es una de las características más destacadas del proyecto.

### Arquitectura del Factory

```python
# 1. Interfaz Abstracta
class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

# 2. Factory con Registry
class ReportFactory:
    _registry: Dict[str, Type[ReportGenerator]] = {}
    _instances: Dict[str, ReportGenerator] = {}  # Singleton cache
    
    @classmethod
    def register(cls, format_name: str):
        """Decorator para registrar generadores"""
        def decorator(generator_class):
            cls._registry[format_name.lower()] = generator_class
            return generator_class
        return decorator
    
    @classmethod
    def create_generator(cls, format: str) -> ReportGenerator:
        """Crea el generador apropiado según el formato"""
        if format not in cls._registry:
            raise ValueError(f"Unsupported format: {format}")
        
        # Singleton: reutiliza instancia si existe
        if format not in cls._instances:
            cls._instances[format] = cls._registry[format]()
        
        return cls._instances[format]
```

### Implementación de Generadores

```python
# PDF Generator
@ReportFactory.register('pdf')
class PDFReportGenerator(ReportGenerator):
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Genera PDF usando ReportLab
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        # ... construcción del PDF
        return {
            'content': buffer.getvalue(),
            'filename': f'reporte_{datetime.now().strftime("%Y%m%d")}.pdf',
            'content_type': 'application/pdf'
        }

# HTML Generator
@ReportFactory.register('html')
class HTMLReportGenerator(ReportGenerator):
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Genera HTML usando Jinja2
        template = env.get_template('report_template.html')
        html_content = template.render(data)
        return {
            'content': html_content.encode('utf-8'),
            'filename': f'reporte_{datetime.now().strftime("%Y%m%d")}.html',
            'content_type': 'text/html'
        }

# JSON Generator
@ReportFactory.register('json')
class JSONReportGenerator(ReportGenerator):
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Genera JSON directamente
        json_content = json.dumps(data, indent=2, ensure_ascii=False)
        return {
            'content': json_content.encode('utf-8'),
            'filename': f'reporte_{datetime.now().strftime("%Y%m%d")}.json',
            'content_type': 'application/json'
        }
```

### Uso del Factory

```python
# En el servicio
from app.factories.report_factory import ReportFactory

# Crear generador según formato solicitado
generator = ReportFactory.create_generator(format='pdf')
report = generator.generate(report_data)

# Retornar respuesta HTTP
return Response(
    content=report['content'],
    media_type=report['content_type'],
    headers={'Content-Disposition': f'attachment; filename={report["filename"]}'}
)
```

### Ventajas de esta Implementación

1. **Open/Closed Principle**: Nuevos formatos se agregan sin modificar código existente
2. **Extensibilidad**: Agregar un nuevo formato (ej: Excel) solo requiere crear una nueva clase y registrarla
3. **Desacoplamiento**: El código cliente no conoce las implementaciones concretas
4. **Singleton**: Reutilización de instancias para optimizar recursos
5. **Type Safety**: Type hints y ABC garantizan contratos claros

---

## 📦 Instalación y Configuración

### Prerrequisitos

- **Docker** y **Docker Compose** instalados
- **Git** para clonar el repositorio
- (Opcional) **Python 3.11+** y **Node.js 18+** para desarrollo local

### Clonar el Repositorio

```bash
git clone https://github.com/YOUR_USERNAME/sia-sofka.git
cd sia-sofka
```

### Configuración de Variables de Entorno

#### Backend

Crea un archivo `.env` en `backend/`:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/sia_sofka_db
DATABASE_URL_SYNC=postgresql://postgres:postgres@db:5432/sia_sofka_db

# Security
SECRET_KEY=your-secret-key-here-change-in-production-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=SIA SOFKA U
APP_VERSION=1.0.0
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000
```

#### Frontend

Crea un archivo `.env` en `frontend/` (opcional, tiene valores por defecto):

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

---

## 🚀 Ejecución del Proyecto

### Opción 1: Docker Compose (Recomendado)

Esta es la forma más sencilla de levantar todo el proyecto:

```bash
# Desde la raíz del proyecto
docker-compose up -d
```

Esto levantará:
- **PostgreSQL** en `localhost:5432`
- **Backend API** en `http://localhost:8000`
- **Frontend** en `http://localhost:3000`

#### Verificar que todo está funcionando

```bash
# Ver logs de todos los servicios
docker-compose logs -f

# Ver logs solo del backend
docker-compose logs -f api

# Ver logs solo del frontend
docker-compose logs -f frontend

# Ver logs solo de la base de datos
docker-compose logs -f db

# Verificar estado de los contenedores
docker-compose ps
```

#### Detener los servicios

```bash
docker-compose down
```

#### Reconstruir contenedores (después de cambios)

```bash
# Detener y eliminar contenedores
docker-compose down

# Reconstruir imágenes
docker-compose build

# Levantar nuevamente
docker-compose up -d
```

### Opción 2: Desarrollo Local (Sin Docker)

#### Backend

```bash
cd backend

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurar variables de entorno (crear .env)
# Ver sección de configuración arriba

# Ejecutar migraciones (si usas Alembic)
alembic upgrade head

# Ejecutar servidor de desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en `http://localhost:8000`
- API Docs (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

#### Frontend

```bash
cd frontend

# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

El frontend estará disponible en `http://localhost:3000`

#### Base de Datos (PostgreSQL)

Si no usas Docker, necesitas tener PostgreSQL instalado y ejecutar:

```bash
# Crear base de datos
createdb sia_sofka_db

# O usando psql
psql -U postgres
CREATE DATABASE sia_sofka_db;
```

Luego actualiza `DATABASE_URL` en el `.env` del backend para apuntar a tu instancia local.

### Crear Usuario Administrador Inicial

Después de levantar el backend, crea un usuario administrador:

```bash
# Si usas Docker
docker-compose exec api python create_admin.py

# Si desarrollas localmente
cd backend
python create_admin.py
```

Esto creará un admin con:
- Email: `admin@sofka.edu.co`
- Password: `admin123` (cambiar en producción)

---

## 🧪 Testing

### Backend

#### Ejecutar Todos los Tests

```bash
cd backend

# Con Docker
docker-compose exec api pytest

# Localmente
pytest
```

#### Ejecutar Tests con Coverage

```bash
# Con Docker
docker-compose exec api pytest --cov=app --cov-report=html --cov-report=term

# Localmente
pytest --cov=app --cov-report=html --cov-report=term
```

#### Ver Reporte de Coverage

```bash
# El reporte HTML se genera en backend/htmlcov/index.html
# Abrir en navegador:
# Windows:
start htmlcov/index.html
# macOS:
open htmlcov/index.html
# Linux:
xdg-open htmlcov/index.html
```

#### Ejecutar Tests Específicos

```bash
# Solo tests unitarios
pytest tests/unit/

# Solo tests de integración
pytest tests/integration/

# Test específico
pytest tests/unit/test_services.py::test_create_user

# Tests que coincidan con un patrón
pytest -k "test_user" -v
```

#### Usando Scripts de Desarrollo

**Windows (PowerShell):**
```powershell
cd backend
.\dev.ps1 test              # Ejecutar todos los tests
.\dev.ps1 test-cov          # Tests con coverage
.\dev.ps1 test-unit         # Solo unitarios
.\dev.ps1 test-integration  # Solo integración
```

**Linux/macOS (Makefile):**
```bash
cd backend
make test              # Ejecutar todos los tests
make test-cov          # Tests con coverage
make test-unit         # Solo unitarios
make test-integration  # Solo integración
```

### E2E con Playwright (carpeta `e2e/`)

Los tests E2E están en **`e2e/`** en la raíz del proyecto (fuera de `frontend/` y `backend/`).

```powershell
# Instalación (primera vez) - desde la raíz
.\e2e\install-playwright.ps1
# O: cd e2e && npm install && npx playwright install

# Ejecutar tests (desde e2e/)
cd e2e
npm run test:e2e

# Modo UI
npm run test:e2e:ui

# Modo headed (ver navegador)
npm run test:e2e:headed

# Ver reporte
npm run test:e2e:report
```

Requisitos: backend en `http://localhost:8000`, frontend en `http://localhost:5173`.

---

## 🔄 CI/CD Pipeline

El proyecto utiliza **GitHub Actions** para automatizar el proceso de CI/CD.

### Pipeline de Backend

El pipeline se ejecuta automáticamente en cada push y pull request. Incluye:

1. **Linting**: Verificación con `flake8`
2. **Formateo**: Verificación con `black` e `isort`
3. **Type Checking**: Verificación con `mypy`
4. **Tests**: Ejecución de todos los tests
5. **Coverage**: Verificación de cobertura mínima (80%)

### Ejecutar Pipeline Localmente

Puedes simular el pipeline localmente antes de hacer push:

**Windows:**
```powershell
cd backend
.\dev.ps1 ci
```

**Linux/macOS:**
```bash
cd backend
make ci
```

Esto ejecutará todas las verificaciones del pipeline.

### Ver Pipeline en GitHub

1. Ve a tu repositorio en GitHub
2. Click en la pestaña **Actions**
3. Selecciona el workflow que quieres ver
4. Revisa los logs de cada job

### Archivo de Pipeline

El pipeline está configurado en `.github/workflows/ci.yml`. Puedes revisarlo para entender qué hace cada paso.

---

## 🤝 AI Collaboration Log

Esta sección documenta interacciones clave donde el desarrollador humano corrigió o mejoró sugerencias de la IA, demostrando el proceso colaborativo de desarrollo.

### Ejemplo 1: Optimización de Queries N+1 en `subjects.py`

**Contexto**: La IA había implementado un endpoint que cargaba estudiantes de una materia usando un loop que generaba múltiples queries a la base de datos (problema N+1).

**Código Original (IA):**
```python
async def _get_students_for_role(...):
    # ...
    enrollments = await enrollment_repo.get_by_subject(subject_id)
    students = []
    for enrollment in enrollments:  # ❌ N+1 queries
        estudiante = await user_service.get_user_by_id(enrollment.estudiante_id)
        if estudiante:
            students.append(estudiante)
    return students
```

**Problema Identificado**: Cada iteración del loop ejecutaba una query adicional para obtener el estudiante, resultando en N+1 queries (1 para enrollments + N para estudiantes).

**Corrección Aplicada (Humano):**
```python
async def _get_students_for_role(...):
    # ...
    # ✅ Usar eager loading para cargar estudiantes en una sola query
    enrollments = await enrollment_repo.get_many_with_relations(
        subject_id=subject_id,
        relations=['estudiante']  # Eager load estudiantes
    )
    # Extraer estudiantes de enrollments (ya cargados)
    students = [
        enrollment.estudiante 
        for enrollment in enrollments 
        if hasattr(enrollment, 'estudiante') and enrollment.estudiante
    ]
    return students
```

**Resultado**: Reducción de N+1 queries a solo 2 queries (1 para enrollments con join, 1 para estudiantes relacionados). Mejora significativa en performance, especialmente con muchos estudiantes.

**Lección Aprendida**: Siempre revisar queries en loops y usar eager loading cuando sea posible. SQLAlchemy ofrece `selectinload` y `joinedload` específicamente para esto.

---

### Ejemplo 2: Manejo de Transacciones en `create_subject`

**Contexto**: La IA había implementado el endpoint de creación de materias con manejo manual de commits y refreshes, lo cual no era necesario y podía causar problemas de consistencia.

**Código Original (IA):**
```python
@router.post("", response_model=SubjectResponse)
async def create_subject(...):
    # ...
    subject = Subject(...)
    db.add(subject)
    await db.commit()
    await db.refresh(subject, ["profesor"])  # ❌ Refresh manual
    
    # Luego intentaba serializar directamente
    return SubjectResponse.model_validate(subject)  # Podía fallar
```

**Problema Identificado**: 
1. El commit manual no era necesario (el servicio ya lo maneja)
2. El refresh manual podía fallar si la relación no estaba cargada correctamente
3. La serialización directa podía fallar con errores de "MissingGreenlet" si las relaciones no estaban cargadas

**Corrección Aplicada (Humano):**
```python
@router.post("", response_model=SubjectResponse)
async def create_subject(...):
    # ...
    # El servicio maneja el commit internamente
    subject = await admin_service.create_subject(subject_data)
    
    # ✅ Usar eager loading para cargar relaciones después del commit
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    
    stmt = (
        select(Subject)
        .where(Subject.id == subject.id)
        .options(selectinload(Subject.profesor))
    )
    result = await db.execute(stmt)
    subject_with_profesor = result.scalar_one()
    
    # ✅ Usar serializer para garantizar serialización correcta
    from app.api.v1.serializers.subject_serializer import SubjectSerializer
    serialized = await SubjectSerializer.serialize_batch([subject_with_profesor], db)
    return serialized[0]
```

**Resultado**: 
- Eliminación de código duplicado (commit ya en servicio)
- Uso correcto de eager loading para relaciones
- Serialización robusta usando el módulo dedicado
- Eliminación de errores de "MissingGreenlet"

**Lección Aprendida**: 
1. Confiar en la separación de responsabilidades: si el servicio maneja commits, no duplicar esa lógica en el endpoint
2. Usar eager loading explícito cuando se necesitan relaciones después de operaciones de escritura
3. Centralizar serialización en módulos dedicados para mantener consistencia

---

**Nota**: Estos ejemplos demuestran cómo la colaboración humano-IA resulta en código más eficiente, mantenible y robusto. La IA proporciona la estructura inicial y el humano aporta optimizaciones basadas en conocimiento del dominio y mejores prácticas.

---

## 📚 Documentación Adicional

- [Historias de Usuario](./HISTORIAS_USUARIO.md) - Historias de usuario siguiendo principios INVEST
- [Casos de Prueba](./CASOS_PRUEBA.md) - Casos de prueba derivados de las historias
- [Backend README](./backend/README.md) - Documentación detallada del backend
- [Frontend README](./frontend/README.md) - Documentación detallada del frontend
- [CI/CD Documentation](./backend/CI_CD.md) - Documentación del pipeline

---

## 📄 Licencia

Este proyecto es privado y de uso interno.

---

## 👥 Contribuidores

- **Desarrollador Principal**: JULIAN ALVAREZ
- **IA Assistant**: Claude (Anthropic)

---

**Última actualización**: Enero 2025  
**Versión**: 1.0.0
