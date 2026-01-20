---
goal: Implementar Sistema de Horarios de Clase con Calendario Visual
version: 1.0
date_created: 2026-01-19
last_updated: 2026-01-19
owner: Equipo de Desarrollo SIA SOFKA
status: Planned
tags: [feature, horarios, calendario, tdd, backend, frontend, validaciones]
---

# Sistema de Horarios y Calendario - Plan de Implementación

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Sistema de gestión de horarios de clases con validación de conflictos (aulas y profesores) y calendario visual semanal para visualizar la distribución de clases.

## 1. Requirements & Constraints

### Requisitos Funcionales

- **REQ-001**: Administrador puede crear horarios de clase con asignatura, aula, día, hora inicio/fin
- **REQ-002**: Validar que no haya solapamiento de horarios para un aula en mismo día/hora
- **REQ-003**: Validar que profesor no tenga clases simultáneas
- **REQ-004**: Validar que estudiantes matriculados no tengan clases simultáneas
- **REQ-005**: Calendario visual semanal mostrando horarios por día (Lunes a Sábado)
- **REQ-006**: Profesor visualiza su horario semanal asignado
- **REQ-007**: Estudiante visualiza su horario semanal basado en inscripciones
- **REQ-008**: Exportar horarios a PDF

### Requisitos Técnicos

- **TEC-001**: Validación de solapamiento usando intervalos de tiempo (PostgreSQL)
- **TEC-002**: Calendario visual con biblioteca React (FullCalendar o react-big-calendar)
- **TEC-003**: Bloques de 30 minutos para granularidad de horarios
- **TEC-004**: Colores diferenciados por asignatura en calendario

### Constraints

- **CON-001**: Horarios de 6:00 AM a 10:00 PM (16 horas diarias)
- **CON-002**: Bloques mínimos de 1 hora, máximos de 4 horas
- **CON-003**: Un aula no puede usarse simultáneamente
- **CON-004**: Un profesor no puede estar en dos lugares al mismo tiempo
- **CON-005**: Respeta arquitectura en capas existente

### Business Rules

- **BUS-001**: Conflicto de horario = solapamiento de tiempo >= 1 minuto
- **BUS-002**: Horarios se definen por semestre/período académico
- **BUS-003**: Horarios solo editables antes de iniciar semestre
- **BUS-004**: Estudiante hereda horarios de asignaturas inscritas

## 2. Implementation Steps

### Fase 1: Modelos de Base de Datos

- **GOAL-001**: Crear modelos para aulas y horarios

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-001  | Crear modelo Classroom (aula) con capacidad y ubicación                    | x         | 2026-01-19 |
| TASK-002  | Crear modelo Schedule con asignatura, aula, día, hora_inicio, hora_fin     | x         | 2026-01-19 |
| TASK-003  | Agregar constraint unique para (asignatura_id, dia_semana, hora_inicio)    | x         | 2026-01-19 |
| TASK-004  | Crear índices en (aula_id, dia_semana, hora_inicio)                        | x         | 2026-01-19 |
| TASK-005  | Generar migración Alembic y ejecutar upgrade                               | x         | 2026-01-19 |

### Fase 2: Repository con Validaciones

- **GOAL-002**: Implementar queries de validación de conflictos

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-006  | Crear ScheduleRepository con query de solapamiento de aulas                | x         | 2026-01-19 |
| TASK-007  | Implementar query de solapamiento de profesor                              | x         | 2026-01-19 |
| TASK-008  | Implementar query de solapamiento de estudiante                            | x         | 2026-01-19 |
| TASK-009  | Crear método get_weekly_schedule(user_id, role)                            | x         | 2026-01-19 |

### Fase 3: Service con Lógica de Negocio

- **GOAL-003**: Implementar validaciones y cálculos de horarios

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-010  | Crear ScheduleService con validate_schedule_conflicts()                    | x         | 2026-01-19 |
| TASK-011  | Implementar lógica de detección de solapamiento con intervalos             | x         | 2026-01-19 |
| TASK-012  | Implementar get_professor_schedule() para vista de profesor                | x         | 2026-01-19 |
| TASK-013  | Implementar get_student_schedule() basado en enrollments                   | x         | 2026-01-19 |

### Fase 4: API Endpoints

- **GOAL-004**: Crear endpoints REST para CRUD de horarios

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-014  | POST /api/v1/schedules - Crear horario con validaciones                    |           |      |
| TASK-015  | GET /api/v1/schedules/weekly - Obtener horarios semanales                  |           |      |
| TASK-016  | PUT /api/v1/schedules/{id} - Actualizar horario                            |           |      |
| TASK-017  | DELETE /api/v1/schedules/{id} - Eliminar horario                           |           |      |
| TASK-018  | GET /api/v1/schedules/classroom/{id} - Ver horarios de aula                |           |      |

### Fase 5: Frontend - Calendario Visual

- **GOAL-005**: Desarrollar componente de calendario con React

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-019  | Instalar react-big-calendar: npm install react-big-calendar date-fns       |           |      |
| TASK-020  | Crear componente WeeklyCalendar.jsx con vista semanal                      |           |      |
| TASK-021  | Implementar transformación de datos Schedule → eventos de calendario       |           |      |
| TASK-022  | Agregar colores por asignatura usando hash de ID                           |           |      |
| TASK-023  | Implementar modal para ver detalles de horario al hacer click              |           |      |
| TASK-024  | Crear componente ScheduleForm.jsx para crear/editar horarios               |           |      |

### Fase 6: Testing - Validaciones Críticas

- **GOAL-006**: Probar validaciones de conflictos exhaustivamente

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-025  | Test: Detectar solapamiento exacto de aulas (mismo inicio/fin)             |           |      |
| TASK-026  | Test: Detectar solapamiento parcial de aulas (inicio dentro de rango)      |           |      |
| TASK-027  | Test: Permitir horarios consecutivos sin solapamiento                      |           |      |
| TASK-028  | Test: Detectar conflicto de profesor en horarios simultáneos               |           |      |
| TASK-029  | Test: Validar que estudiante no tenga clases simultáneas                   |           |      |
| TASK-030  | Test E2E: Admin crea horario y aparece en calendario visual                |           |      |

### Fase 7: Exportación PDF

- **GOAL-007**: Generar PDF de horarios semanales

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-031  | Instalar reportlab para generación de PDFs                                 |           |      |
| TASK-032  | Crear SchedulePDFGenerator con tabla de horarios                           |           |      |
| TASK-033  | Endpoint GET /api/v1/schedules/export/pdf                                  |           |      |

## 3. Alternatives

- **ALT-001**: Usar FullCalendar en lugar de react-big-calendar - Ambas son viables, elegir según licencia
- **ALT-002**: Validar conflictos en frontend antes de enviar - Implementar validación dual (frontend + backend)
- **ALT-003**: Permitir solapamientos con advertencia - No implementar, rechazar estrictamente

## 4. Dependencies

- **DEP-001**: Modelo Asignatura (Subject) existente
- **DEP-002**: Modelo User con rol Profesor
- **DEP-003**: Sistema de inscripciones (Enrollment)
- **DEP-004**: react-big-calendar (npm package)
- **DEP-005**: date-fns para manejo de fechas

## 5. Files

- **FILE-001**: backend/app/models/schedule.py - Modelos Classroom y Schedule
- **FILE-002**: backend/app/schemas/schedule.py - Schemas Pydantic
- **FILE-003**: backend/app/repositories/schedule_repository.py
- **FILE-004**: backend/app/services/schedule_service.py
- **FILE-005**: backend/app/api/v1/endpoints/schedules.py
- **FILE-006**: frontend/src/components/schedule/WeeklyCalendar.jsx
- **FILE-007**: frontend/src/components/schedule/ScheduleForm.jsx

## 6. Testing

- **TEST-001**: test_detect_classroom_overlap() - Solapamiento de aulas
- **TEST-002**: test_detect_professor_overlap() - Conflicto profesor
- **TEST-003**: test_allow_consecutive_schedules() - Horarios consecutivos válidos
- **TEST-004**: test_get_student_schedule() - Horario basado en inscripciones
- **TEST-005**: Pruebas E2E - Crear horario y visualizar en calendario

## 7. Risks & Assumptions

- **RISK-001**: Cálculo de solapamiento complejo - Usar operadores de intervalo de PostgreSQL
- **RISK-002**: Performance con muchos horarios - Indexar correctamente
- **ASSUMPTION-001**: Aulas físicas tienen código único
- **ASSUMPTION-002**: Horarios no cambian durante el semestre

## 8. Related Specifications

- [README.md](../README.md)
- [AGENTS.md](../AGENTS.md)
- [React Big Calendar Docs](https://jquense.github.io/react-big-calendar/)
