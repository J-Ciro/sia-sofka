# TODO: feature horarios-calendario - Paso a paso

Guía para continuar la implementación. Hacer **commit con conventional-commits** al final de cada fase de TDD.

**Siguiente paso:** Fase 6 (Testing – Validaciones críticas).

---

## ✅ Hecho

- **Fase 1**: `Classroom`, `Schedule`, migración Alembic, tests `test_schedule_models.py`
- **Fase 2**: `ScheduleRepository` (overlaps + `get_weekly_schedule`), tests `test_schedule_repository.py`
- **Fase 3**: `ScheduleService`, schemas, tests `test_schedule_service.py`
- **Fase 4**: REST `schedules` (POST, GET /weekly, PUT, DELETE, GET /classroom/{id}), `ScheduleConflictError`, tests async en repo/servicio, `test_schedules_endpoints.py`
- **Fase 5**: `GET /classrooms`, `WeeklyCalendar.jsx`, `ScheduleForm.jsx`, ruta `/horarios`, menú; `react-big-calendar`, `date-fns`

---

## 📋 Fase 3: ScheduleService (TDD) ✅

**Objetivo**: TASK-010 a TASK-013. **Completado.**

### 3.1 RED – Tests (hecho)

1. `backend/tests/unit/test_schedule_service.py`:
   - `test_validate_schedule_conflicts_sin_conflictos` → `validate_schedule_conflicts` devuelve `[]`
   - `test_validate_schedule_conflicts_conflicto_aula` → devuelve error tipo "classroom"
   - `test_validate_schedule_conflicts_conflicto_profesor` → devuelve error tipo "professor"
   - `test_validate_schedule_conflicts_conflicto_estudiante` → devuelve error tipo "student" (opcional si se valida)
   - `test_get_professor_schedule` → delega en `repo.get_weekly_schedule(user_id, PROFESOR)`
   - `test_get_student_schedule` → delega en `repo.get_weekly_schedule(user_id, ESTUDIANTE)`

2. Ejecutar: `pytest backend/tests/unit/test_schedule_service.py -v -m unit` → debe fallar (no existe `ScheduleService`).

### 3.2 GREEN – Implementación

3. Crear `backend/app/schemas/schedule.py`:
   - `ScheduleCreate`: `subject_id`, `classroom_id`, `dia_semana`, `hora_inicio`, `hora_fin`
   - `ScheduleUpdate`: mismos campos opcionales
   - `ScheduleResponse`: `id`, `codigo`, `subject_id`, `classroom_id`, `dia_semana`, `hora_inicio`, `hora_fin`, `subject`, `classroom` (opcionales anidados)

4. Crear `backend/app/services/schedule_service.py`:
   - `__init__(self, db: Session)` (o compatible con inyección)
   - `validate_schedule_conflicts(subject_id, classroom_id, dia_semana, hora_inicio, hora_fin, exclude_schedule_id=None) -> list[dict]`  
     - Obtener `profesor_id` de `Subject`.  
     - Llamar `repo.find_classroom_overlaps`, `find_professor_overlaps` (y opcional `find_student_overlaps`).  
     - Si hay resultados, devolver `[{"type": "classroom"|"professor"|"student", "schedules": [...]}]`.
   - `get_professor_schedule(profesor_id) -> list[Schedule]` → `repo.get_weekly_schedule(profesor_id, UserRole.PROFESOR)`
   - `get_student_schedule(estudiante_id) -> list[Schedule]` → `repo.get_weekly_schedule(estudiante_id, UserRole.ESTUDIANTE)`
   - Opcional: `create_schedule(data: ScheduleCreate)`, `get_by_id`, `update`, `delete` (o dejarlos para Fase 4 con el endpoint).

5. Registrar en `backend/app/services/__init__.py` si aplica.

6. Ejecutar tests hasta que pasen.

### 3.3 Commit

```bash
git add backend/app/schemas/schedule.py backend/app/services/schedule_service.py backend/tests/unit/test_schedule_service.py backend/app/services/__init__.py
git commit -m "feat(schedule): add ScheduleService and schemas (Fase 3)"
```

---

## 📋 Fase 4: API Endpoints

**Objetivo**: TASK-014 a TASK-018.

### 4.1 Dependencias y router

1. En `backend/app/api/v1/__init__.py`:  
   - `from app.api.v1.endpoints import schedules`  
   - `api_router.include_router(schedules.router, prefix="/schedules", tags=["schedules"])`

2. Crear `backend/app/api/v1/endpoints/schedules.py`:
   - `Depends(get_db)` → si el proyecto usa `AsyncSession`, hacer `get_db` async o usar adaptador; si todo es sync, usar `Session` desde un `get_db` sync.
   - Dependencia para “usuario actual” (p. ej. `get_current_user`) y verificación de rol Admin para crear/editar/eliminar.

### 4.2 Endpoints

3. **POST /api/v1/schedules** (TASK-014)  
   - Body: `ScheduleCreate`.  
   - Llamar `ScheduleService.validate_schedule_conflicts`; si hay conflictos → `422` con detalle.  
   - Si no hay conflictos: crear `Schedule` (codigo se genera en modelo), devolver `ScheduleResponse`.

4. **GET /api/v1/schedules/weekly** (TASK-015)  
   - Query opcional: `?role=Profesor|Estudiante` o derivar del usuario.  
   - Si Admin: opción de `?user_id=` para ver otro usuario.  
   - Llamar `get_professor_schedule` o `get_student_schedule` según rol.  
   - Devolver lista de `ScheduleResponse`.

5. **PUT /api/v1/schedules/{id}** (TASK-016)  
   - Body: `ScheduleUpdate`.  
   - Validar conflictos con `exclude_schedule_id=id`.  
   - Actualizar y devolver `ScheduleResponse`.

6. **DELETE /api/v1/schedules/{id}** (TASK-017)  
   - Eliminar y devolver `204` o cuerpo vacío.

7. **GET /api/v1/schedules/classroom/{id}** (TASK-018)  
   - Añadir en `ScheduleRepository`: `get_by_classroom(classroom_id) -> list[Schedule]`.  
   - Endpoint que devuelve horarios de ese aula.

### 4.3 Tests y commit

8. Añadir tests en `backend/tests/integration/test_schedules_endpoints.py` (o similar) para al menos POST con/sin conflictos y GET weekly.

9. Commit:
   ```bash
   git add backend/app/api/v1/endpoints/schedules.py backend/app/api/v1/__init__.py backend/tests/integration/test_schedules_endpoints.py
   git commit -m "feat(schedule): add REST endpoints for schedules (Fase 4)"
   ```

---

## 📋 Fase 5: Frontend – Calendario

**Objetivo**: TASK-019 a TASK-024.

### 5.1 Dependencias

1. `cd frontend && npm install react-big-calendar date-fns` (TASK-019).

### 5.2 Componentes

2. **WeeklyCalendar.jsx** (TASK-020, TASK-021, TASK-022, TASK-023):
   - Vista `week` de `react-big-calendar`.
   - `events`: transformar `GET /api/v1/schedules/weekly` a `{ start, end, title, resource: { schedule } }`.
   - `eventPropGetter`: color por `subject.id` (hash o mapa de colores).
   - `onSelectEvent`: abrir modal con detalle (código, materia, profesor, aula, hora, duración).

3. **ScheduleForm.jsx** (TASK-024):
   - Campos: Materia (select), Aula (select), Día, Hora inicio, Hora fin.
   - Cargar opciones desde `GET /api/v1/subjects`, `GET /api/v1/classrooms` (crear endpoint `GET /api/v1/classrooms` si no existe).
   - Submit → `POST /api/v1/schedules`; si 422, mostrar errores de conflicto.

4. Ruta y menú: p. ej. `/horarios` o `/schedules` y enlace en el layout.

5. Commit:
   ```bash
   git add frontend/package.json frontend/package-lock.json frontend/src/components/schedule/
   git commit -m "feat(schedule): add WeeklyCalendar and ScheduleForm (Fase 5)"
   ```

---

## 📋 Fase 6: Tests de validaciones

**Objetivo**: TASK-025 a TASK-030.

1. **Backend** (TASK-025–029):  
   - Asegurar que `test_schedule_repository` y `test_schedule_service` cubran:  
     - solapamiento exacto de aulas,  
     - solapamiento parcial,  
     - consecutivos sin solapamiento,  
     - conflicto de profesor,  
     - conflicto de estudiante.

2. **E2E** (TASK-030):  
   - En `frontend/tests/e2e/`:  
     - Login como Admin, ir a horarios, crear horario, comprobar que aparece en el calendario.

3. Commit:
   ```bash
   git add backend/tests/ frontend/tests/
   git commit -m "test(schedule): overlap and E2E for schedules (Fase 6)"
   ```

---

## 📋 Fase 7: Exportación PDF

**Objetivo**: TASK-031 a TASK-033.

1. `pip install reportlab` en `backend/requirements.txt` (TASK-031).

2. `SchedulePDFGenerator`:  
   - Entrada: lista de `Schedule` (o DTOs).  
   - Tabla: día, hora, materia, profesor, aula.  
   - Método `generate(stream)` o `generate_bytes()` (TASK-032).

3. **GET /api/v1/schedules/export/pdf** (TASK-033):  
   - Query: `?user_id=`, `?role=`, `?classroom_id=` (filtrar horarios).  
   - Llamar a `SchedulePDFGenerator` y devolver `Content-Type: application/pdf` y `Content-Disposition: attachment`.

4. Opcional: botón “Exportar PDF” en `WeeklyCalendar` que llame a este endpoint.

5. Commit:
   ```bash
   git add backend/requirements.txt backend/app/ backend/tests/
   git commit -m "feat(schedule): PDF export for schedules (Fase 7)"
   ```

---

## 📋 Extras

- **Classroom CRUD**: si no existe, añadir `GET/POST /api/v1/classrooms` y repo/servicio para `Classroom` (usado en `ScheduleForm`).
- **Plan**: actualizar `plan/feature-horarios-calendario-1.md` marcando con `x` y fecha las tareas completadas.
- **Linter**: `black`, `isort`, `flake8` en los archivos tocados antes de cada commit.

---

## Comandos útiles

```bash
# Backend
cd backend
pytest tests/unit/test_schedule_*.py -v -m unit
pytest tests/integration/ -v -k schedule
alembic upgrade head

# Frontend
cd frontend
npm run dev
npm run test:e2e
```
