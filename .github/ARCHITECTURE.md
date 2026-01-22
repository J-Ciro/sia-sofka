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
  - Key endpoints: `attendance.py`, `schedules.py`, `classrooms.py`, `users.py` (bulk import)
- **Service Layer** (`app/services/`):
  - Contains business logic
  - Role-specific services: `AdminService`, `ProfesorService`, `EstudianteService`
  - Feature services: `AttendanceService`, `ScheduleService`, `BulkImportService`
- **Repository Layer** (`app/repositories/`):
  - Abstracts data access using the Repository pattern
  - All repositories inherit from `AbstractRepository[Model]`
  - Uses Mixins (`EagerLoadMixin`, `PaginationMixin`) for reusable logic
  - Consistent error handling via `@handle_repository_errors` decorator
  - Key repositories: `AttendanceRepository`, `ScheduleRepository`, `UserRepository`
- **Model Layer** (`app/models/`):
  - SQLAlchemy ORM models (async)
  - Key models: `Attendance`, `ClaseSession`, `Schedule`, `Classroom`

**Key Patterns:**
- **Factory + Registry**: For report generation (PDF/HTML/JSON) via `ReportFactory`
- **Repository Pattern**: Abstract CRUD with `AbstractRepository[Model]` base class
  - All repositories inherit from `AbstractRepository` with Mixins
  - `EagerLoadMixin`: Automatic relationship loading
  - `PaginationMixin`: Pagination validation and helpers
  - `@handle_repository_errors`: Centralized error handling decorator
- **Mixin Pattern**: Reusable logic for eager loading, pagination, filtering
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
  - `components/`: 
    - `auth/`: Authentication components
    - `dashboard/`: Dashboard pages (Users, Subjects, Grades, etc.)
    - `attendance/`: Attendance management (TakeAttendance, SessionHistory, StudentAttendanceHistory)
    - `schedule/`: Schedule & calendar (CalendarContainer, WeeklyCalendar, MonthlyCalendar, ScheduleForm)
    - `layout/`: Layout components (DashboardLayout, Sidebar)
    - `modals/`: Modal dialogs (BulkImportModal, UserModal, etc.)
    - `common/`: Reusable components (Loading, StatsCard, TimeInput)
  - `services/`: API communication (axios) - attendanceService, scheduleService, etc.
  - `context/`: React Context for global state (AuthContext)
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
- **Repository Refactoring**: All repositories now inherit from `AbstractRepository[Model]` with Mixins
  - Reduces code duplication (~150 lines per repository)
  - Ensures consistent CRUD operations
  - Standardizes error handling and pagination
- **Testing**: Isolated, independent tests; no shared state

---

## 7. Security & Validation

- **Authentication**: JWT, bcrypt
- **Authorization**: Role-based
- **Input Validation**: Pydantic schemas
- **Sanitization**: XSS prevention utilities
- **No raw SQL**: Always use SQLAlchemy ORM

---

## 8. Current Features

### Implemented Features
- **User Management**: CRUD operations for students and professors
- **Subject Management**: Subject catalog with professor assignment
- **Enrollment Management**: Student enrollment tracking
- **Grade Management**: Multi-role grade recording and viewing
- **Report Generation**: PDF/HTML/JSON report generation via Factory pattern
- **Manual Attendance System**: 
  - Session creation and management
  - Bulk and individual attendance marking
  - Attendance analytics and percentage calculations
  - Alert system for low attendance (<80%, <70%)
- **Schedule & Calendar Management**:
  - Weekly and monthly calendar views
  - Classroom assignment and management
  - Schedule conflict detection
  - Time slot management
- **Bulk Import/Export**:
  - Excel import for users (students/professors)
  - Excel export functionality
  - Template generation and validation

## 9. References
- [README.md](../README.md)
- [AGENTS.md](../AGENTS.md)
- [PRODUCT.md](PRODUCT.md)
- [MEJORAS_REFACTORIZACION_REPOSITORIOS.md](../MEJORAS_REFACTORIZACION_REPOSITORIOS.md)
- [backend/app/api/v1/](../backend/app/api/v1/)
- [backend/app/factories/report_factory.py](../backend/app/factories/report_factory.py)
- [backend/app/repositories/base.py](../backend/app/repositories/base.py)
- [backend/app/repositories/mixins.py](../backend/app/repositories/mixins.py)

---

*For more details, see the referenced files and documentation in the repository.*
