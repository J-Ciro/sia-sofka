# Agent Development Guidelines for SIA SOFKA

This document provides comprehensive guidelines for AI coding agents working on the SIA SOFKA project - a full-stack academic management system with FastAPI backend and React frontend.

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
npm run dev                     # Start development server (localhost:3000)

# Building
npm run build                   # Production build
npm run preview                 # Preview production build

# Testing (Playwright E2E)
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
- **Documentation**: Markdown files in `/documentation` folder

## Common Patterns to Follow

1. **Repository Pattern** for data access
2. **Factory Pattern** for object creation (reports, users)
3. **Context API** for global state management
4. **Async/Await** for all asynchronous operations
5. **Error Boundaries** for React error handling
6. **Dependency Injection** via FastAPI's DI system

Follow these guidelines to maintain consistency and quality across the SIA SOFKA codebase.