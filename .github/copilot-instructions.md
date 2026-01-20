# SIA SOFKA - AI Coding Agent Instructions

> **Cursor / agentes de IA**: Este archivo puede referenciarse con `@.github/copilot-instructions.md` para que Cursor y otros agentes lo carguen como contexto. Mantener formato Markdown y rutas relativas al repo.

## Project Overview
Full-stack academic management system with FastAPI backend (Python 3.11+) and React 18 frontend. Follows Clean Architecture with strict layered separation: API → Services → Repositories → Models.

## Architecture Patterns

### Backend: Layered Architecture (4 layers)
- **API Layer** (`app/api/v1/endpoints/`): REST endpoints, request validation, response serialization
- **Service Layer** (`app/services/`): Business logic, role-specific operations (AdminService, ProfesorService, EstudianteService)
- **Repository Layer** (`app/repositories/`): Data access using AbstractRepository + Mixins (EagerLoadMixin, PaginationMixin)
- **Model Layer** (`app/models/`): SQLAlchemy ORM models with async support

### Key Design Patterns
1. **Factory + Registry Pattern** (`app/factories/report_factory.py`): Report generation (PDF/HTML/JSON) using `@ReportFactory.register('format')` decorator
2. **Repository Pattern** (`app/repositories/base.py`): Abstract CRUD operations with Protocol-based DIP
3. **Mixin Pattern** (`app/repositories/mixins.py`): Reusable eager loading, pagination, filtering logic
4. **Custom Exception Hierarchy** (`app/core/exceptions.py`): BaseAppException → NotFoundError, ValidationError, UnauthorizedError

### SOLID y patrones: cuándo aplicar (evitar sobre‑ingeniería)

Aplicar SOLID y patrones **solo cuando sea necesario o viable**. Omitir en casos triviales para no generar complejidad innecesaria.

| Principio | Aplicar cuando… | Omitir / simplificar cuando… |
|-----------|------------------|------------------------------|
| **S** (Single Responsibility) | Servicios, repositorios, componentes con lógica clara: una responsabilidad por clase/módulo. | Funciones helpers o DTOs simples; no fragmentar en exceso. |
| **O** (Open/Closed) | Variantes que crecerán: `ReportFactory` (nuevos formatos), estrategias de exportación, validadores intercambiables. | Solo 1–2 implementaciones previstas y estables; no crear jerarquías “por si acaso”. |
| **L** (Liskov) | Herencia real: repos base → repos concretos, `BaseAppException` → excepciones específicas. | No hay sustitución de subtipos; evitar herencia solo por reutilizar código. |
| **I** (Interface Segregation) | Protocolos/abstractas para repos, estrategias o plugins con contratos acotados. | Una sola implementación; interfaces gigantes “por si acaso”. |
| **D** (Dependency Inversion) | Servicios que reciben repos, FastAPI `Depends`, pruebas con mocks. | Un único implementation sin alternativas (tests, variantes); no abstraer “por norma”. |

**Patrones:** usar cuando aporten extensibilidad o claridad; **no** cuando añadan capas sin beneficio.

- **Repository**: Siempre para acceso a datos (ya en uso).
- **Factory/Registry**: Múltiples variantes (PDF/HTML/JSON, etc.). No para crear un solo tipo de objeto.
- **Strategy**: Comportamiento intercambiable (validación, exportación, formatos). No para una sola estrategia.
- **Mixin**: Lógica reutilizable (eager load, paginación). No para un solo uso.
- **Decorator**: Cross‑cutting (logging, cache, retry). No para un solo punto de uso.
- **Observer/Eventos**: Múltiples consumidores desacoplados (ej. notificaciones tras crear usuario). No para flujos síncronos y simples.

Si añadir un patrón o abstracción no simplifica el cambio futuro ni la lectura, preferir implementación directa. Más detalle: [AGENTS.md](AGENTS.md#solid-and-design-patterns-when-to-apply).

## Critical Workflows

### Backend Development
```bash
# Start development server (must use --reload for auto-restart)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Testing with coverage requirement (80% minimum)
pytest                           # Run all tests
pytest -m unit                   # Unit tests only
pytest -m integration            # Integration tests only
pytest --cov=app --cov-fail-under=80

# Code quality (pre-commit hooks enforce these)
black app/ tests/                # Format (line-length 120)
isort app/ tests/                # Sort imports (profile=black)
mypy app/                        # Type checking (python 3.11+)

# Database migrations (always use Alembic, never raw SQL)
alembic upgrade head
alembic revision --autogenerate -m "description"
```

### Frontend Development
```bash
cd frontend
npm run dev                      # Dev server on localhost:5173
```

### E2E Tests (Playwright, carpeta `e2e/`)
```bash
cd e2e
npm run test:e2e                 # Playwright E2E tests
npm run test:e2e:ui              # Interactive test mode
```

### Docker Development
```bash
# Full stack (recommended for testing integrations)
docker-compose up --build        # Backend on :8000, Frontend on :3000
docker-compose exec api python create_admin.py  # Create admin user
```

## Code Conventions

### Python Type Hints (Required)
```python
# Use modern union syntax (Python 3.11+)
async def get_user(self, user_id: int) -> User | None:

# Pydantic field validation
email: EmailStr
nombre: str = Field(..., min_length=1, max_length=100)
```

### Import Order (enforced by isort)
```python
# 1. Standard library
from typing import Optional
# 2. Third-party
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
# 3. Local app
from app.repositories.user_repository import UserRepository
```

### Custom Exceptions (Always use these, never raise HTTPException directly)
```python
# In services layer
if not user:
    raise NotFoundError("User", user_id)
if existing_email:
    raise ValidationError("Email already exists")
```

### Repository Pattern Usage
```python
# Services MUST use repositories, never query directly
class AdminService:
    def __init__(self, db: AsyncSession, admin_user: User):
        self.user_service = UserService(db)  # Compose services
        self.enrollment_repo = EnrollmentRepository(db)  # Use repos
    
    async def get_user_with_grades(self, user_id: int):
        # Use mixins for eager loading
        return await self.user_repo._get_one_with_relations(
            User, User.id == user_id, relations=['enrollments.grades']
        )
```

### Factory Pattern Registration
```python
# Register new report formats without modifying factory
@ReportFactory.register('pdf')
class PDFReportGenerator(ReportGenerator):
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Implementation
```

### React Component Structure
```javascript
// Functional components, hooks at top, event handlers before render
const Users = () => {
  const [users, setUsers] = useState([])
  const { user } = useAuth()  // Context hooks
  
  useEffect(() => { fetchUsers() }, [])  // Effects after hooks
  
  const handleCreate = async (data) => { }  // Event handlers
  
  return <div className="container mx-auto px-4">...</div>
}
```

## Security & Validation

- **Authentication**: JWT tokens via `app/core/security.py`, passwords hashed with bcrypt
- **Authorization**: Role-based (Admin/Profesor/Estudiante) validated in service layer
- **Input Sanitization**: `app/core/sanitizers.py` for XSS prevention
- **Never use raw SQL**: Always use SQLAlchemy ORM for query safety

## Testing Requirements

- **Minimum 80% coverage** (enforced by pytest config)
- **Mark tests**: `@pytest.mark.unit` or `@pytest.mark.integration`
- **Use fixtures**: Database setup in `tests/conftest.py`
- **Async tests**: `pytest-asyncio` with `asyncio_mode = auto`

## Integration Points

- **Database**: PostgreSQL with async SQLAlchemy (asyncpg driver)
- **CORS**: Configured for localhost:3000/3001 in `app/main.py`
- **API Communication**: Frontend uses axios via `src/services/` layer
- **Rate Limiting**: Optional SlowAPI integration in `app/core/rate_limit.py`

## Common Pitfalls

1. **Don't bypass service layer**: Controllers must call services, not repositories directly
2. **Always use type hints**: Mypy runs in CI pipeline
3. **Async consistency**: Use `async/await` for all DB operations
4. **Migration safety**: Test migrations with `alembic upgrade/downgrade` before committing
5. **Role-specific services**: Use AdminService/ProfesorService/EstudianteService, not generic UserService for role-specific operations

## File References
- Architecture overview: [README.md](README.md#-arquitectura)
- Full agent guidelines (SOLID, patrones, Cursor): [AGENTS.md](AGENTS.md)
- API structure: [backend/app/api/v1/](backend/app/api/v1/)
- Factory pattern: [backend/app/factories/report_factory.py](backend/app/factories/report_factory.py)
- Repository mixins: [backend/app/repositories/mixins.py](backend/app/repositories/mixins.py)
