# SIA SOFKA – System Architecture Overview

## 1. Introduction
SIA SOFKA is a full-stack academic management system designed for educational institutions. It features a robust, scalable backend built with FastAPI (Python 3.11+) and a modern React 18 frontend. The system follows Clean Architecture principles, ensuring strict separation of concerns and maintainability.

---

## 2. High-Level Architecture

```
+-------------------+         +-------------------+         +-------------------+
|    Frontend       | <-----> |     API Layer     | <-----> |   Service Layer   |
| (React 18, Vite)  |  HTTP   | (FastAPI, REST)   |  Logic  |  (Business Logic) |
+-------------------+         +-------------------+         +-------------------+
                                                                |
                                                                v
                                                    +-----------------------+
                                                    |  Repository Layer     |
                                                    | (Data Access, ORM)    |
                                                    +-----------------------+
                                                                |
                                                                v
                                                    +-----------------------+
                                                    |   Model Layer         |
                                                    | (SQLAlchemy ORM)      |
                                                    +-----------------------+
```

---

## 3. Backend Architecture (FastAPI)

**Layered Structure:**
- **API Layer** (`app/api/v1/endpoints/`):
  - Exposes REST endpoints
  - Handles request validation and response serialization
- **Service Layer** (`app/services/`):
  - Contains business logic
  - Role-specific services: `AdminService`, `ProfesorService`, `EstudianteService`
- **Repository Layer** (`app/repositories/`):
  - Abstracts data access using the Repository pattern
  - Uses Mixins for eager loading, pagination, filtering
- **Model Layer** (`app/models/`):
  - SQLAlchemy ORM models (async)

**Key Patterns:**
- **Factory + Registry**: For report generation (PDF/HTML/JSON) via `ReportFactory`
- **Repository Pattern**: Abstract CRUD with Protocol-based DIP
- **Mixin Pattern**: Reusable logic for eager loading, pagination
- **Custom Exception Hierarchy**: Centralized error handling (`BaseAppException`)

**Other Backend Features:**
- **Authentication**: JWT tokens, bcrypt password hashing
- **Authorization**: Role-based, enforced in service layer
- **Input Sanitization**: XSS prevention utilities
- **Database**: PostgreSQL (async SQLAlchemy, asyncpg driver)
- **Migrations**: Alembic
- **Testing**: Pytest, pytest-asyncio, 80%+ coverage required

---

## 4. Frontend Architecture (React 18)

- **Component-based structure** (in `frontend/src/`):
  - `components/`: Auth, dashboard, layout, modals, common
  - `services/`: API communication (axios)
  - `context/`: React Context for global state
  - `config/`: App configuration
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **E2E Testing**: Playwright (in `e2e/`)

---

## 5. Integration & DevOps

- **Dockerized**: `docker-compose.yml` for full stack (backend, frontend)
- **Pre-commit Hooks**: Enforce formatting (black, isort), linting, type checks
- **CI/CD**: GitHub Actions (workflows in `.github/`)
- **Coverage**: Enforced via pytest config

---

## 6. Design Principles & Patterns

- **Clean Architecture**: Strict separation between API, services, repositories, and models
- **SOLID Principles**: Applied where extensibility/clarity is needed, not for trivial cases
- **Extensibility**: Factory/Registry for report formats, Mixins for reusable logic
- **Testing**: Isolated, independent tests; no shared state

---

## 7. Security & Validation

- **Authentication**: JWT, bcrypt
- **Authorization**: Role-based
- **Input Validation**: Pydantic schemas
- **Sanitization**: XSS prevention utilities
- **No raw SQL**: Always use SQLAlchemy ORM

---

## 8. References
- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [backend/app/api/v1/](backend/app/api/v1/)
- [backend/app/factories/report_factory.py](backend/app/factories/report_factory.py)
- [backend/app/repositories/mixins.py](backend/app/repositories/mixins.py)

---

*For more details, see the referenced files and documentation in the repository.*
