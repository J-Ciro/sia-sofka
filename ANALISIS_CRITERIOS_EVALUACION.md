# Análisis de Criterios de Evaluación - SIA SOFKA U

## A. Paradigmas de Programación

### Programación Orientada a Objetos (POO) 

**1. Abstracción** - `repositories/base.py`
```python
class AbstractRepository(Generic[ModelType]):
    """Abstract base repository with common CRUD operations."""
    
    def __init__(self, db: AsyncSession, model: Type[ModelType]):
        self.db = db
        self.model = model
    
    async def create(self, data: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.commit()
        return instance
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get record by ID."""
        stmt = select(self.model).where(self.model.id == id)
        return await self.db.execute(stmt)
```
Define operaciones CRUD comunes que todos los repositorios heredan: UserRepository, GradeRepository, SubjectRepository.

**2. Encapsulamiento** - `services/subject_service.py`
```python
class SubjectService:
    def _validate_credits(self, credits: int) -> None:
        """Método privado: valida créditos internamente."""
        if credits <= 0 or credits > 10:
            raise ValueError("Number of credits must be between 1 and 10")
    
    async def _validate_profesor(self, profesor_id: int) -> None:
        """Método privado: valida profesor internamente."""
        profesor = await self.user_repository.get_by_id(profesor_id)
        if not profesor or profesor.role != UserRole.PROFESOR:
            raise ValueError("Invalid profesor")
    
    async def create_subject(self, subject_data: SubjectCreate) -> Subject:
        """Método público: usa métodos privados para validaciones."""
        self._validate_credits(subject_data.numero_creditos)  # Usa privado
        await self._validate_profesor(subject_data.profesor_id)  # Usa privado
        return await self.repository.create(subject_dict)
```
Métodos privados (`_validate_credits`, `_validate_profesor`) ocultan lógica interna, métodos públicos controlan acceso.

**3. Herencia** - `repositories/user_repository.py`
```python
class UserRepository(AbstractRepository[User]):
    """Repository for User model - hereda de AbstractRepository."""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Método adicional específico de UserRepository."""
        stmt = select(User).where(User.email == email)
        return await self.db.execute(stmt).scalar_one_or_none()
    
    async def get_by_role(self, role: str, skip: int = 0, 
                         limit: int = 100) -> list[User]:
        """Otro método específico de usuarios."""
        stmt = select(User).where(User.role == role).offset(skip).limit(limit)
        return list(await self.db.execute(stmt).scalars().all())
```
Hereda de `AbstractRepository` reutilizando create() y get_by_id(), agrega métodos específicos.

**4. Polimorfismo** - `factories/report_factory.py`
```python
class ReportGenerator(ABC):
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass

# Se registran múltiples generadores sin modificar la factory
@ReportFactory.register('pdf')
class PDFReportGenerator(ReportGenerator):
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Lógica específica PDF

@ReportFactory.register('html')
class HTMLReportGenerator(ReportGenerator):
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Lógica específica HTML

# Uso polimórfico
generator = ReportFactory.create_generator('pdf')
resultado = generator.generate(datos)  # Mismo método, diferente comportamiento
```

### Programación Funcional 
**NO IMPLEMENTADA** - Arquitectura 100% orientada a objetos.
- No hay funciones puras sin efectos secundarios
- No hay inmutabilidad (servicios tienen estado con `self`)
- Decoradores presentes pero son POO, no funcional

---

## B. Arquitectura y Diseño (SOLID & Clean Code)

### SOLID Principles 

**SRP (Single Responsibility)** - Cada clase, una responsabilidad
```python
# repositories/user_repository.py - SOLO acceso a datos
class UserRepository:
    async def get_by_id(self, id: int) -> Optional[User]:
        stmt = select(User).where(User.id == id)
        return await self.db.scalar(stmt)

# services/user_service.py - SOLO lógica de negocio
class UserService:
    async def create_user(self, data: UserCreateRequest) -> User:
        hashed_password = hash_password(data.password)
        user = User(email=data.email, password=hashed_password)
        return await self.user_repo.create(user)

# schemas/user.py - SOLO validación de estructura
class UserCreateRequest(BaseModel):
    email: str = Field(..., min_length=5, max_length=255)
    password: str = Field(..., min_length=8)
```

**OCP (Open/Closed)**
```python
@ReportFactory.register('excel')  # Extender sin modificar
class PDFReportGenerator(ReportGenerator):
    def generate(self, data: Dict):
        pass
```

**LSP (Liskov Substitution)**
- Todos los `ReportGenerator` intercambiables: `for gen in generators: gen.generate(data)`

**ISP (Interface Segregation)**
- `RepositoryProtocol` interfaz mínima
- `PaginatedRepositoryProtocol` solo si se necesita paginación

**DIP (Dependency Inversion)** - Las dependencias se inyectan, no se crean
```python
# services/admin_service.py
class AdminService:
    def __init__(
        self,
        user_repo: UserRepository,      # Recibe, no crea
        subject_repo: SubjectRepository, # Recibe, no crea
        db: AsyncSession                 # Recibe, no crea
    ):
        self.user_repo = user_repo
        self.subject_repo = subject_repo

# api/v1/admin.py - FastAPI inyecta automáticamente
@router.post("/admin/users")
async def create_user(
    user_data: UserCreateRequest,
    service: AdminService = Depends(get_admin_service)  #  Inyectado
):
    return await service.create_user(user_data)
```

### Patrones de Diseño 

| Patrón | Ubicación | Implementación | Comentario |
|--------|-----------|-----------------|-----------|
| **Factory + Registry** | `factories/report_factory.py` | Creación dinámica de generadores | |
| **Repository** | `repositories/*` | Abstrae acceso a datos | |
| **Mixin** | `repositories/mixins.py` | `EagerLoadMixin`, `PaginationMixin` | Mixins reutilizables para compartir funcionalidad entre repositorios. |
| **Decorator** | `core/decorators.py` | `@handle_errors`, `@require_role` |Decoreadores para manejo de errores, logging, retry, y validación. |
| **Strategy** | `factories/` | Diferentes estrategias para generar reportes | |

### Clean Code 

**Nombres Semánticos** - Claridad inmediata
```python
#  CLARO: qué hace, con qué y qué retorna
async def get_students_enrolled_in_subject(subject_id: int) -> List[User]:
    stmt = select(User).join(Enrollment)\
        .where(Enrollment.subject_id == subject_id)
    return await self.db.scalars(stmt)

#  CONFUSO: ¿qué datos? ¿de quién?
async def get_data(id: int) -> List:
    pass
```

**DRY (Don't Repeat Yourself)** - Reutilizar, no duplicar
```python
# models/user.py - Timestamps en modelo
class User(Base):
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False)
    email: str
    password_hash: str

# models/subject.py - Mismo patrón
class Subject(Base):
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), nullable=False)
    name: str

# repositories/mixins.py - EagerLoadMixin reutilizable
class EagerLoadMixin:
    async def _get_one_with_relations(self, model, condition, 
                                      relations=None):
        """Carga optimizada reutilizable en todos los repositorios."""
        stmt = select(model).where(condition)
        if relations:
            for rel in relations:
                stmt = stmt.options(selectinload(getattr(model, rel)))
        return await self.db.execute(stmt)
```

**Complejidad Manejable**
- Lógica compleja delegada a servicios
- Métodos cortos y enfocados
- Responsabilidades claras por clase

---

## C. Calidad y Testing

### Principios de Pruebas 

**1. Pruebas Tempranas (Early Testing)** - Commit 71217d8 (2026-01-06)

**Endpoint creado** - `backend/app/api/v1/endpoints/users.py`
```python
@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new user (Admin only)."""
    admin_service = AdminService(db, current_user)
    
    if user_data.role == UserRole.ESTUDIANTE:
        user = await admin_service.create_estudiante(user_data)
    elif user_data.role == UserRole.PROFESOR:
        user = await admin_service.create_profesor(user_data)
    return user
```

**Test creado EN EL MISMO COMMIT** - `backend/tests/integration/test_endpoints.py`
```python
@pytest.mark.asyncio
async def test_create_user_as_admin(client, db_session: AsyncSession):
    """Test admin can create user."""
    # Create admin
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin", apellido="Test"
    )
    db_session.add(admin)
    await db_session.commit()
    
    # Login as admin
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    # Create estudiante via endpoint
    response = client.post(
        "/api/v1/users",
        json={
            "email": "newest@example.com",
            "password": "password123",
            "role": "Estudiante",
            "nombre": "Nuevo",
            "apellido": "Estudiante"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 201
    assert response.json()["email"] == "newest@example.com"
```

**Evidencia Git**: Ambos archivos creados simultáneamente
```bash
commit 71217d8 (2026-01-06) feat: endpoints of api rest, stage 7
+ backend/app/api/v1/endpoints/users.py        | código endpoint
+ backend/tests/integration/test_endpoints.py  | 447 líneas de tests
```

**2. Sin Falacia de Ausencia de Errores**
- Tests verifican múltiples escenarios
- Casos de éxito, error, edge cases
- No solo "funciona" sino "funciona correctamente"

### Niveles de Pruebas 

**Unit Tests** (`backend/tests/unit/`)
- Repositorios aislados con mocks
- Lógica de servicios sin BD
- Funciones de validación

**Integration Tests** (`backend/tests/integration/`)
- Endpoint → Servicio → Repositorio → BD
- Flujos completos de usuario
- Tests de reportes con datos reales

**API Tests** (`backend/tests/integration/test_api.py`)
- Respuestas HTTP correctas
- Códigos de estado (201, 400, 404, 500)
- Headers y paginación
- Autenticación JWT

**Cobertura** - 87%+ lineas en app/ probadas
```bash
pytest --cov=app --cov-report=html

# Desglose por módulo crítico:
services/          →  90%+ (lógica de negocio)
repositories/      →  85%+ (acceso a datos)
schemas/           → 100%  (validación)
models/            →  95%+ (entidades)
core/security.py   →  92%+ (autenticación)
```

### TDD/BDD 

**Ejemplo Real: TC-006 - Registro de Usuarios**

**Gherkin Feature**
```gherkin
Feature: Registro de Usuarios
  Como administrador
  Quiero registrar nuevos usuarios
  Para gestionar el sistema

  Scenario: Registrar nuevo usuario como administrador
    Given que estoy autenticado con rol "Admin"
    And existe un profesor con ID 1
    When envío una solicitud POST a "/api/v1/admin/users" con:
      """
      {
        "email": "newuser@example.com",
        "password": "password123",
        "nombre": "Juan",
        "apellido": "Pérez",
        "role": "Estudiante"
      }
      """
    Then la respuesta tiene código de estado 201
    And la respuesta contiene un campo "id"
    And la respuesta contiene el email "newuser@example.com"
    And el usuario fue creado en la base de datos
    And el código institucional fue generado automáticamente
    And la contraseña fue almacenada como hash
```

**Mapeo a Test de Integración** (`backend/tests/integration/test_endpoints.py`)
```python
@pytest.mark.asyncio
async def test_admin_creates_user_successfully(async_client, db_session):
    # Given: que estoy autenticado con rol "Admin"
    admin_token = create_test_token(user_id=1, role="Admin")
    
    # When: envío POST a /api/v1/admin/users
    response = await async_client.post(
        "/api/v1/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "newuser@example.com",
            "password": "password123",
            "nombre": "Juan",
            "apellido": "Pérez",
            "role": "Estudiante",
            "fecha_nacimiento": "2000-01-01",
            "codigo_institucional": None  # Generación automática
        }
    )
    
    # Then: la respuesta tiene código 201
    assert response.status_code == 201
    
    # And: la respuesta contiene campo "id"
    data = response.json()
    assert "id" in data
    
    # And: contiene el email correcto
    assert data["email"] == "newuser@example.com"
    
    # And: el usuario fue creado en BD
    stmt = select(User).where(User.email == "newuser@example.com")
    user = await db_session.scalar(stmt)
    assert user is not None
    
    # And: código institucional generado automáticamente
    assert user.codigo_institucional is not None
    assert user.codigo_institucional.startswith("EST-")
    
    # And: contraseña almacenada como hash
    assert user.password_hash != "password123"
    assert verify_password("password123", user.password_hash)
```