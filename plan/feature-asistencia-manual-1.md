---
goal: Implementar Sistema de Asistencia Manual con Botones Masivos
version: 1.0
date_created: 2026-01-19
last_updated: 2026-01-19
owner: Equipo de Desarrollo SIA SOFKA
status: Planned
tags: [feature, asistencia, tdd, backend, frontend, e2e]
---

# Sistema de Asistencia Manual - Plan de Implementación

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Sistema simple y práctico de control de asistencia donde el profesor toma lista manualmente, con opciones rápidas para marcar todos presentes/ausentes y ajustar individualmente. Genera reportes de ausentismo y alertas automáticas.

## 1. Requirements & Constraints

### Requisitos Funcionales

- **REQ-001**: Profesor debe poder crear sesiones de clase por asignatura
- **REQ-002**: Sistema debe mostrar lista de estudiantes matriculados al crear sesión
- **REQ-003**: Botones "Marcar Todos Presentes", "Marcar Todos Ausentes", "Marcar Todos Tardanza"
- **REQ-004**: Click en estudiante individual cicla estado: Presente → Ausente → Tardanza → Presente
- **REQ-005**: Sistema calcula porcentaje de asistencia automáticamente (Presente + Tardanza + Excusa / Total)
- **REQ-006**: Generar alertas automáticas si asistencia < 80% (warning), < 70% (critical)
- **REQ-007**: Estudiante puede visualizar su historial de asistencia por asignatura
- **REQ-008**: Administrador y profesores ven dashboard de alertas de ausentismo

### Constraints

- **CON-001**: No usar QR ni geolocalización (solo manual)
- **CON-002**: Debe integrarse con sistema de inscripciones existente (Enrollment)
- **CON-003**: Respetar arquitectura en capas: API → Services → Repositories → Models
- **CON-004**: Usar custom exceptions (NotFoundError, ValidationError, UnauthorizedError)

### Security Requirements

- **SEC-001**: Solo profesores pueden crear sesiones y tomar asistencia
- **SEC-002**: Profesor solo accede a sesiones de sus asignaturas
- **SEC-003**: Estudiante solo ve su propia asistencia

## 2. Implementation Steps

### Fase 1: Modelos y Migraciones de Base de Datos

- **GOAL-001**: Crear modelos SQLAlchemy y ejecutar migraciones Alembic

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-001  | Crear modelo ClaseSession en backend/app/models/attendance.py              |           |      |
| TASK-002  | Crear modelo Attendance con relationship a User y ClaseSession             |           |      |
| TASK-003  | Crear modelo AttendanceStats con índices compuestos                        |           |      |
| TASK-004  | Crear modelo AttendanceAlert con campos de nivel y resolución              |           |      |
| TASK-005  | Generar migración Alembic y ejecutar upgrade head                          |           |      |

### Fase 2: Repository y Services

- **GOAL-002**: Implementar lógica de acceso a datos y negocio

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-006  | Crear AttendanceRepository con queries especializadas                      |           |      |
| TASK-007  | Crear AttendanceService con validaciones de negocio                        |           |      |
| TASK-008  | Implementar cálculo de estadísticas y alertas automáticas                  |           |      |

### Fase 3: API y Frontend

- **GOAL-003**: Desarrollar endpoints REST y componentes React

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-009  | Crear endpoints en backend/app/api/v1/endpoints/attendance.py              |           |      |
| TASK-010  | Crear componente TakeAttendance.jsx con botones masivos                    |           |      |
| TASK-011  | Crear componente StudentAttendanceHistory.jsx                              |           |      |

### Fase 4: Testing

- **GOAL-004**: Escribir pruebas con cobertura >85%

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-012  | Escribir 12 pruebas unitarias en test_attendance_service.py                |           |      |
| TASK-013  | Escribir 8 pruebas de integración en test_attendance_endpoints.py          |           |      |
| TASK-014  | Escribir 4 pruebas E2E en frontend/tests/e2e/attendance.spec.js            |           |      |

## 3. Alternatives

- **ALT-001**: Usar registro de asistencia con códigos QR - Descartado por complejidad
- **ALT-002**: Cache de estadísticas con Redis - Pospuesto, usar tabla attendance_stats

## 4. Dependencies

- **DEP-001**: Sistema de inscripciones (Enrollment) operativo
- **DEP-002**: Sistema de autenticación JWT
- **DEP-003**: PostgreSQL 15+ con índices compuestos

## 5. Files

- **FILE-001**: backend/app/models/attendance.py
- **FILE-002**: backend/app/schemas/attendance.py
- **FILE-003**: backend/app/repositories/attendance_repository.py
- **FILE-004**: backend/app/services/attendance_service.py
- **FILE-005**: backend/app/api/v1/endpoints/attendance.py
- **FILE-006**: frontend/src/components/attendance/TakeAttendance.jsx

## 6. Testing

- **TEST-001**: Pruebas unitarias (12 tests) - Cobertura >85%
- **TEST-002**: Pruebas integración (8 tests) - API + BD
- **TEST-003**: Pruebas E2E (4 tests) - Playwright

## 7. Risks & Assumptions

- **RISK-001**: Performance con >500 estudiantes - Mitigación: índices y paginación
- **ASSUMPTION-001**: Tardanza cuenta como asistencia válida
- **ASSUMPTION-002**: Sesión cerrada no se puede modificar

## 8. Related Specifications

- [README.md](../README.md)
- [AGENTS.md](../AGENTS.md)
- [CASOS_PRUEBA_GHERKIN.md](../CASOS_PRUEBA_GHERKIN.md)
