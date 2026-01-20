# Agent Development Guidelines for SIA SOFKA

This document provides comprehensive guidelines for AI coding agents working on the SIA SOFKA project - a full-stack academic management system with FastAPI backend and React frontend.

## Critical Evolution Rules

**El nuevo código no debe afectar al código existente; debe complementarlo.**

- **Extender, no reemplazar**: Añadir funcionalidad, endpoints, componentes o tests sin alterar el comportamiento actual de lo ya implementado.
- **Contratos estables**: No cambiar firmas de funciones, esquemas de API o contratos ya usados por otros módulos o tests; extender con parámetros opcionales o nuevos endpoints si hace falta.
- **Código legado intacto**: Si se refactoriza, asegurar que las rutas, servicios y componentes existentes sigan funcionando como antes.

**Los tests que se creen jamás deben afectar a los demás.**

- **Tests aislados**: Cada test debe ser independiente; no depender del orden de ejecución ni del estado dejado por otro test.
- **Sin efectos colaterales entre tests**: Usar fixtures, `setUp`/`tearDown` o bases de datos en memoria/transacciones que se reinician por test; evitar estado global compartido que un test modifique y otro espere.
- **Nuevos tests sin romper existentes**: Al añadir tests, los ya existentes deben seguir pasando; si un test nuevo obliga a cambiar o desactivar otros, replantear el diseño del test (datos, mocks, alcance).

## Project Structure

```
sia-sofka/
├── backend/           # Python FastAPI backend
├── frontend/          # React frontend application  
├── .github/           # GitHub Actions workflows
├── docker-compose.yml # Container orchestration
└── documentation/     # Project documentation
```

## Build, Test & Development Commands

### Backend (Python/FastAPI)
```bash
# Development
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing
pytest                          # Run all tests
pytest tests/test_file.py       # Run specific test file
pytest -k "test_function"       # Run specific test by name
pytest -m unit                  # Run unit tests only
pytest -m integration           # Run integration tests only
pytest --cov=app                # Run with coverage report

# Code Quality
black app/ tests/               # Format code
isort app/ tests/               # Sort imports
flake8 app/ tests/              # Lint code
mypy app/                       # Type checking
pre-commit run --all-files      # Run all pre-commit hooks

# Database
alembic upgrade head            # Run migrations
alembic revision --autogenerate -m "Description"  # Create new migration
```

### Frontend (React/Vite)
```bash
# Development
cd frontend
npm run dev                     # Start development server (localhost:5173)

# Building
npm run build                   # Production build
npm run preview                 # Preview production build
```

### E2E (Playwright, carpeta `e2e/`)
```bash
# Desde la raíz: .\e2e\install-playwright.ps1  (primera vez)
cd e2e
npm run test:e2e                # Run E2E tests
npm run test:e2e:ui             # Run tests with UI mode
npm run test:e2e:headed         # Run tests in headed browser
npm run test:e2e:debug          # Debug specific test
npm run test:e2e:report         # View test report
npm run test:e2e:codegen        # Generate test code
```

### Docker
```bash
# Full stack development
docker-compose up               # Start all services
docker-compose up --build      # Rebuild and start
docker-compose down             # Stop all services
docker-compose logs -f backend  # View backend logs
```

## Code Style Guidelines

### Python Backend Standards

#### Import Organization
```python
# Standard library imports
import asyncio
from typing import Optional

# Third-party imports  
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

# Local app imports
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserUpdate
from app.models.user import User
```

#### Naming Conventions
- **Classes**: PascalCase (`UserService`, `UserRepository`)
- **Functions/Methods**: snake_case (`create_user`, `get_by_email`)
- **Variables**: snake_case (`user_data`, `codigo_institucional`)
- **Constants**: SCREAMING_SNAKE_CASE (`MAX_FILE_SIZE`)
- **Private methods**: Leading underscore (`_validate_email`)

#### Type Hints
```python
# Modern union syntax preferred
async def get_user_by_id(self, user_id: int) -> User | None:

# Specific return types
async def get_users(self, skip: int = 0, limit: int = 100) -> list[User]:

# Pydantic fields with validation
email: EmailStr
nombre: str = Field(..., min_length=1, max_length=100)
fecha_nacimiento: date = Field(..., description="Birth date")
```

#### Error Handling
```python
# Custom exception hierarchy
class BaseAppException(HTTPException):
    """Base exception for application errors."""

class NotFoundError(BaseAppException):
    def __init__(self, resource: str, identifier: str | int):
        detail = f"{resource} with id {identifier} not found"
        super().__init__(detail=detail, status_code=404)

# Usage in services
try:
    user = await self.user_repository.get_by_id(user_id)
    if not user:
        raise NotFoundError("User", user_id)
except ValueError as e:
    raise ValidationError(str(e))
```

#### Documentation
```python
def create_user(self, user_data: UserCreate) -> User:
    """Create a new user with business logic validation.
    
    Args:
        user_data: User creation data with all required fields
    
    Returns:
        Created user instance with generated institutional code
    
    Raises:
        ValueError: If email already exists or invalid role
        ValidationError: If required fields are missing
    """
```

### React Frontend Standards

#### Import Organization
```javascript
// React and core libraries first
import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'

// Third-party libraries
import axios from 'axios'
import { Mail, Lock } from 'lucide-react'

// Local context and hooks
import { useAuth } from '../../context/AuthContext'

// Component imports (relative paths)
import Login from './components/auth/Login'
import Header from '../layout/Header'
```

#### Component Structure
```javascript
// Functional components with descriptive names
const UserDashboard = () => {
  // Hooks at the top
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const { isAuthenticated } = useAuth()

  // Effect hooks
  useEffect(() => {
    fetchUsers()
  }, [])

  // Event handlers
  const handleUserCreate = async (userData) => {
    // Implementation
  }

  // Render method
  return (
    <div className="container mx-auto px-4">
      {/* Component JSX */}
    </div>
  )
}

export default UserDashboard
```

#### Props and State
```javascript
// Destructured props with defaults
const StatsCard = ({ title, value, icon: Icon, color = 'primary' }) => {

// Consistent state naming
const [formData, setFormData] = useState({
  email: '',
  password: '',
  nombre: ''
})

// Error and loading states
const [error, setError] = useState('')
const [isSubmitting, setIsSubmitting] = useState(false)
```

#### Styling with Tailwind
```javascript
// Utility-first approach
className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-50 to-purple-100"

// Configuration objects for reusable styles
const colorConfig = {
  primary: {
    bg: 'bg-gradient-to-br from-purple-500 to-purple-600',
    iconBg: 'bg-purple-100',
    iconColor: 'text-purple-600'
  },
  success: {
    bg: 'bg-gradient-to-br from-green-500 to-green-600',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600'
  }
}

// Conditional styling
className={`px-3 py-1.5 text-xs font-semibold rounded-full ${
  user.role === 'Admin' ? 'bg-purple-600 text-white' :
  user.role === 'Profesor' ? 'bg-blue-600 text-white' :
  'bg-green-600 text-white'
}`}
```

## Architecture Patterns

### Backend Architecture (Clean Architecture)
```
backend/app/
├── api/v1/              # Presentation Layer
│   ├── endpoints/       # REST API endpoints
│   ├── serializers/     # Response serialization
│   └── validators/      # Request validation
├── services/            # Business Logic Layer
├── repositories/        # Data Access Layer
├── models/              # SQLAlchemy Database Models
├── schemas/             # Pydantic Schemas
├── core/                # Configuration & Security
└── utils/               # Helper Utilities
```

### Frontend Architecture (Component-Based)
```
frontend/src/
├── components/
│   ├── auth/           # Authentication components
│   ├── dashboard/      # Dashboard pages
│   ├── layout/         # Layout components
│   ├── modals/         # Modal dialogs
│   └── common/         # Reusable components
├── services/           # API service layer
├── context/            # React Context providers
└── config/             # App configuration
```

## SOLID and Design Patterns (When to Apply)

Apply SOLID and design patterns **only when necessary or viable**. Omit them in trivial cases to avoid over-engineering. Prefer simple, direct implementations when an abstraction does not improve future changes or readability.

### SOLID Principles

| Principle | Apply when… | Omit or simplify when… |
|-----------|-------------|-------------------------|
| **S** (Single Responsibility) | Services, repositories, components with clear logic: one responsibility per class/module. | Simple helpers or DTOs; avoid excessive fragmentation. |
| **O** (Open/Closed) | Variants that will grow: `ReportFactory` (new formats), export strategies, interchangeable validators. | Only 1–2 stable implementations; do not create hierarchies "just in case". |
| **L** (Liskov Substitution) | Real inheritance: base repos → concrete repos, `BaseAppException` → specific exceptions. | No subtype substitution; avoid inheritance only to reuse code. |
| **I** (Interface Segregation) | Protocols/abstracts for repos, strategies, or plugins with focused contracts. | Single implementation; avoid large "just in case" interfaces. |
| **D** (Dependency Inversion) | Services receiving repos, FastAPI `Depends`, tests with mocks. | One implementation with no alternatives; do not abstract "by default". |

### Design Patterns: When to Use

- **Repository**: Always for data access (already in use).
- **Factory/Registry**: Multiple variants (e.g. PDF/HTML/JSON). Not for creating a single object type.
- **Strategy**: Interchangeable behavior (validation, export, formats). Not for a single strategy.
- **Mixin**: Reusable logic (eager load, pagination). Not for a one-off use.
- **Decorator**: Cross-cutting (logging, cache, retry). Not for a single use site.
- **Observer/Events**: Multiple decoupled consumers (e.g. notifications after user creation). Not for simple synchronous flows.

If adding a pattern or abstraction does not make future changes or reading easier, prefer a direct implementation. See also [.github/copilot-instructions.md](.github/copilot-instructions.md) for a compact reference.

## Development Guidelines

### Code Quality Requirements
- **Test Coverage**: Minimum 80% for backend code
- **Type Safety**: All Python functions must have type hints
- **Error Handling**: All async operations must handle exceptions
- **Pre-commit Hooks**: Code must pass all quality checks before commit

### API Design
- **REST Endpoints**: Follow RESTful conventions
- **Request/Response**: Use Pydantic schemas for validation
- **Status Codes**: Use appropriate HTTP status codes
- **Authentication**: JWT token-based authentication required

### Database
- **Migrations**: Use Alembic for schema changes
- **Relationships**: Define proper SQLAlchemy relationships
- **Async**: Use async patterns for all database operations
- **Validation**: Database constraints + Pydantic validation

### Testing Strategy
- **Unit Tests**: Test business logic in isolation
- **Integration Tests**: Test API endpoints with database
- **E2E Tests**: Playwright tests for user workflows
- **Coverage**: Monitor and maintain test coverage
- **Aislamiento entre tests** (ver *Critical Evolution Rules*): Los tests nuevos no deben afectar a los existentes; cada test ha de ser independiente, sin estado compartido ni dependencia del orden de ejecución. Si un test nuevo hace fallar otros, corregir el nuevo test (fixtures, mocks, alcance), no desactivar ni modificar los que ya pasaban.

### Security Guidelines
- **Authentication**: JWT tokens with proper expiration
- **Passwords**: Bcrypt hashing with salt
- **Input Validation**: Pydantic schemas for all inputs
- **SQL Injection**: Use SQLAlchemy ORM, never raw SQL

## File and Directory Conventions

- **Python Files**: snake_case.py (`user_service.py`)
- **JavaScript Files**: PascalCase for components (`UserDashboard.jsx`)
- **Test Files**: `test_*.py` for Python, `*.test.js` for JavaScript
- **Configuration**: Keep in root or dedicated config directories


## Common Patterns to Follow

1. **Repository Pattern** for data access
2. **Factory Pattern** for object creation when multiple variants exist (e.g. reports); see SOLID and Design Patterns above when in doubt
3. **Context API** for global state management
4. **Async/Await** for all asynchronous operations
5. **Error Boundaries** for React error handling
6. **Dependency Injection** via FastAPI's DI system

Apply SOLID and extra patterns only when they add value; avoid over-engineering. Follow these guidelines to maintain consistency and quality across the SIA SOFKA codebase.