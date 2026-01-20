---
goal: Implementar Sistema de Importación y Exportación Masiva de Usuarios vía Excel
version: 1.0
date_created: 2026-01-19
last_updated: 2026-01-19
owner: Equipo de Desarrollo SIA SOFKA
status: Planned
tags: [feature, excel, import, export, bulk-upload, pandas, openpyxl]
---

# Sistema de Import/Export Excel - Plan de Implementación

![Status: Planned](https://img.shields.io/badge/status-Planned-blue)

Permite a administradores cargar/actualizar estudiantes masivamente desde Excel con lógica upsert (crear/actualizar), y exportar usuarios actuales a Excel para edición offline.

## 1. Requirements & Constraints

### Requisitos Funcionales

- **REQ-001**: Botón "Importar Excel" para cargar archivo .xlsx con estudiantes
- **REQ-002**: Lógica Upsert: Si email existe → actualiza datos; Si es nuevo → crea usuario
- **REQ-003**: Botón "Exportar a Excel" descarga usuarios actuales en formato editable
- **REQ-004**: Validación estricta de columnas requeridas antes de procesar
- **REQ-005**: Reporte detallado: "X creados, Y actualizados, Z errores con detalles"
- **REQ-006**: Plantilla Excel descargable con estructura correcta
- **REQ-007**: No exportar contraseñas (seguridad)
- **REQ-008**: Generar código institucional automáticamente para nuevos estudiantes

### Campos Requeridos en Excel

- **email**: EmailStr (único)
- **password**: string (min 8 caracteres) - Solo para nuevos, no actualiza existentes
- **nombre**: string (1-100 caracteres)
- **apellido**: string (1-100 caracteres)
- **rol**: "Estudiante" (fijo)
- **fecha_nacimiento**: date (formato YYYY-MM-DD)
- **numero_contacto**: string (10-20 caracteres)
- **programa_academico**: string (1-200 caracteres)
- **ciudad_residencia**: string (1-100 caracteres)

### Requisitos Técnicos

- **TEC-001**: Backend usa pandas para parsear Excel
- **TEC-002**: Backend usa openpyxl para generar Excel
- **TEC-003**: Frontend usa FormData para upload de archivos
- **TEC-004**: Validación con Pydantic antes de procesar cada fila
- **TEC-005**: Transacción atómica: todo o nada (rollback on error)

### Constraints

- **CON-001**: Solo rol "Estudiante" permitido en importación masiva
- **CON-002**: Máximo 1000 filas por archivo
- **CON-003**: Tamaño máximo archivo: 5 MB
- **CON-004**: Solo archivos .xlsx (no .xls legacy)
- **CON-005**: Emails duplicados dentro del mismo archivo → error

### Security Requirements

- **SEC-001**: Solo administradores pueden importar/exportar
- **SEC-002**: Passwords hasheadas con bcrypt antes de guardar
- **SEC-003**: No exportar campo password_hash (seguridad)
- **SEC-004**: Validar extensión de archivo en backend
- **SEC-005**: Sanitizar datos de Excel contra XSS

### Business Rules

- **BUS-001**: Upsert basado en email único
- **BUS-002**: Al actualizar, password no se modifica (mantener existente)
- **BUS-003**: Código institucional formato: EST-YYYY-NNNN (ej: EST-2026-0001)
- **BUS-004**: Si error en cualquier fila, rechazar todo el archivo
- **BUS-005**: Fecha de nacimiento debe ser pasada (no futura)

## 2. Implementation Steps

### Fase 1: Backend - Schemas y Validaciones

- **GOAL-001**: Definir schemas Pydantic para validación de filas

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-001  | Crear EstudianteImportRow schema en backend/app/schemas/bulk_import.py     |           |      |
| TASK-002  | Agregar validators: email, fecha_nacimiento, rol="Estudiante"              |           |      |
| TASK-003  | Crear BulkImportResult schema con created/updated/errors                   |           |      |
| TASK-004  | Crear BulkImportError schema para detalles de errores por fila             |           |      |

### Fase 2: Backend - Service de Importación

- **GOAL-002**: Implementar lógica de parseo y upsert

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-005  | Crear BulkImportService en backend/app/services/bulk_import_service.py     |           |      |
| TASK-006  | Implementar parse_excel() usando pandas.read_excel()                       |           |      |
| TASK-007  | Implementar validate_rows() con Pydantic validation                        |           |      |
| TASK-008  | Implementar bulk_import_students() con lógica upsert                       |           |      |
| TASK-009  | Implementar _check_existing_user(email) para detectar duplicados           |           |      |
| TASK-010  | Implementar _generate_codigo_institucional() con formato EST-YYYY-NNNN     |           |      |
| TASK-011  | Agregar transacción atómica con rollback on error                          |           |      |

### Fase 3: Backend - Service de Exportación

- **GOAL-003**: Implementar generación de archivos Excel

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-012  | Implementar export_users_to_excel(role) en BulkImportService               |           |      |
| TASK-013  | Query usuarios con pandas DataFrame                                        |           |      |
| TASK-014  | Excluir campo password_hash de exportación                                 |           |      |
| TASK-015  | Generar Excel con openpyxl usando df.to_excel()                            |           |      |
| TASK-016  | Retornar BytesIO para descarga directa                                     |           |      |

### Fase 4: Backend - API Endpoints

- **GOAL-004**: Crear endpoints REST para upload/download

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-017  | POST /api/v1/users/bulk-import con UploadFile                              |           |      |
| TASK-018  | GET /api/v1/users/export?role=Estudiante con StreamingResponse             |           |      |
| TASK-019  | GET /api/v1/users/template para descargar plantilla vacía                  |           |      |
| TASK-020  | Agregar validación de content-type y tamaño de archivo                     |           |      |
| TASK-021  | Configurar CORS para permitir multipart/form-data                          |           |      |

### Fase 5: Frontend - Componente de Importación

- **GOAL-005**: Desarrollar UI para upload y feedback

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-022  | Crear BulkImportModal.jsx en frontend/src/components/users/                |           |      |
| TASK-023  | Implementar input file con accept=".xlsx"                                  |           |      |
| TASK-024  | Implementar handleImport() con FormData y axios                            |           |      |
| TASK-025  | Mostrar progress bar durante upload                                        |           |      |
| TASK-026  | Mostrar resumen de resultados: X creados, Y actualizados                   |           |      |
| TASK-027  | Mostrar lista de errores con número de fila y descripción                  |           |      |
| TASK-028  | Botón "Exportar Usuarios" para descargar Excel                             |           |      |
| TASK-029  | Botón "Descargar Plantilla" para template vacío                            |           |      |

### Fase 6: Plantilla Excel

- **GOAL-006**: Crear plantilla descargable con headers

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-030  | Crear estudiantes_template.xlsx en frontend/public/templates/              |           |      |
| TASK-031  | Definir headers: email, password, nombre, apellido, etc.                   |           |      |
| TASK-032  | Agregar 2 filas de ejemplo con datos válidos                               |           |      |
| TASK-033  | Agregar hoja "Instrucciones" con guía de uso                               |           |      |

### Fase 7: Testing - Validaciones

- **GOAL-007**: Probar casos de éxito y error exhaustivamente

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-034  | Test: parse_valid_excel_file() retorna lista de EstudianteImportRow        |           |      |
| TASK-035  | Test: import_creates_new_users() crea registros en BD                      |           |      |
| TASK-036  | Test: import_updates_existing_users() actualiza sin cambiar password       |           |      |
| TASK-037  | Test: import_rejects_invalid_rows() con email inválido                     |           |      |
| TASK-038  | Test: import_rejects_duplicate_emails_in_file()                            |           |      |
| TASK-039  | Test: export_users_to_excel() genera archivo válido                        |           |      |
| TASK-040  | Test: export_excludes_passwords() no incluye campo password                |           |      |

### Fase 8: Testing - Integración API

- **GOAL-008**: Probar endpoints con archivos reales

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-041  | Test: upload_excel_creates_users() POST con archivo válido                 |           |      |
| TASK-042  | Test: upload_invalid_excel_rejects() retorna 400 con errores               |           |      |
| TASK-043  | Test: export_users_endpoint() GET retorna archivo Excel                    |           |      |
| TASK-044  | Test: unauthorized_user_cannot_import() retorna 403                        |           |      |
| TASK-045  | Test: file_too_large_rejected() supera límite de 5 MB                      |           |      |

### Fase 9: Testing - E2E Playwright

- **GOAL-009**: Probar flujo completo de usuario

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-046  | Test: Admin importa estudiantes desde Excel y ve resultado                 |           |      |
| TASK-047  | Test: Admin exporta usuarios actuales y descarga Excel                     |           |      |
| TASK-048  | Test: Admin intenta importar Excel inválido y ve errores                   |           |      |
| TASK-049  | Crear fixtures con archivos Excel de prueba válidos/inválidos              |           |      |

### Fase 10: Documentación y Deployment

- **GOAL-010**: Documentar funcionalidad y preparar para producción

| Task      | Description                                                                 | Completed | Date |
|-----------|-----------------------------------------------------------------------------|-----------|------|
| TASK-050  | Actualizar README.md con sección de Importación Masiva                     |           |      |
| TASK-051  | Crear guía de usuario con capturas de pantalla                             |           |      |
| TASK-052  | Documentar formato de plantilla Excel en Wiki                              |           |      |
| TASK-053  | Agregar ejemplo de Excel en documentación                                  |           |      |
| TASK-054  | Code review y merge a develop                                              |           |      |

## 3. Alternatives

- **ALT-001**: Usar CSV en lugar de Excel - Descartado, Excel es más amigable para usuarios finales
- **ALT-002**: Permitir actualización de contraseñas en import - Descartado por seguridad
- **ALT-003**: Procesamiento asíncrono con Celery - Pospuesto para v2.0, usar síncrono inicialmente
- **ALT-004**: Importar múltiples roles (no solo Estudiante) - Pospuesto, implementar solo Estudiante primero

## 4. Dependencies

- **DEP-001**: pandas >= 2.0 (backend) para parseo de Excel
- **DEP-002**: openpyxl >= 3.1 (backend) para generación de Excel
- **DEP-003**: Modelo User existente con validaciones
- **DEP-004**: Sistema de autenticación JWT para validar admin
- **DEP-005**: bcrypt para hashing de contraseñas

## 5. Files

### Backend - Nuevos Archivos

- **FILE-001**: backend/app/schemas/bulk_import.py - Schemas de validación
- **FILE-002**: backend/app/services/bulk_import_service.py - Lógica de import/export
- **FILE-003**: backend/app/api/v1/endpoints/bulk_import.py - Endpoints REST

### Backend - Modificados

- **FILE-004**: backend/requirements.txt - Agregar pandas, openpyxl

### Frontend - Nuevos Archivos

- **FILE-005**: frontend/src/components/users/BulkImportModal.jsx - Modal de importación
- **FILE-006**: frontend/public/templates/estudiantes_template.xlsx - Plantilla descargable

### Frontend - Modificados

- **FILE-007**: frontend/src/components/dashboard/Users.jsx - Agregar botón "Importar Excel"

### Testing

- **FILE-008**: backend/tests/unit/services/test_bulk_import_service.py - Tests unitarios
- **FILE-009**: backend/tests/integration/api/test_bulk_import_endpoints.py - Tests integración
- **FILE-010**: frontend/tests/e2e/bulk-import.spec.js - Tests E2E
- **FILE-011**: frontend/tests/e2e/fixtures/estudiantes_validos.xlsx - Fixture válido
- **FILE-012**: frontend/tests/e2e/fixtures/estudiantes_invalidos.xlsx - Fixture con errores

## 6. Testing

### Pruebas Unitarias (backend/tests/unit/)

- **TEST-001**: test_parse_valid_excel_file() - Parseo exitoso con pandas
- **TEST-002**: test_import_creates_new_users() - Crear 5 usuarios nuevos
- **TEST-003**: test_import_updates_existing_users() - Actualizar sin cambiar password
- **TEST-004**: test_import_rejects_invalid_rows() - Email inválido rechazado
- **TEST-005**: test_import_rejects_duplicate_emails() - Duplicados dentro de archivo
- **TEST-006**: test_export_users_to_excel() - Generar DataFrame y Excel
- **TEST-007**: test_export_excludes_passwords() - Campo password no incluido
- **TEST-008**: test_generate_codigo_institucional() - Formato EST-YYYY-NNNN

### Pruebas de Integración (backend/tests/integration/)

- **TEST-009**: test_upload_excel_creates_users() - POST con multipart/form-data
- **TEST-010**: test_upload_invalid_excel_rejects() - Retorna 400 con errores
- **TEST-011**: test_export_users_endpoint() - GET descarga Excel válido
- **TEST-012**: test_unauthorized_access() - 403 para no-admin
- **TEST-013**: test_file_too_large_rejected() - Límite de 5 MB

### Pruebas E2E (frontend/tests/e2e/)

- **TEST-014**: Admin importa estudiantes válidos - Flujo completo
- **TEST-015**: Admin exporta usuarios - Descarga archivo
- **TEST-016**: Admin ve errores con Excel inválido - Mensaje detallado

### Cobertura Esperada

- **Cobertura mínima**: 85%
- **Archivos críticos**: 95% (bulk_import_service.py)

## 7. Risks & Assumptions

### Riesgos

- **RISK-001**: Archivos Excel corruptos pueden crashear pandas
  - **Mitigación**: Try-catch con manejo de excepciones específicas
  
- **RISK-002**: Memoria insuficiente con archivos muy grandes (>1000 filas)
  - **Mitigación**: Límite estricto de 1000 filas, procesar en chunks si necesario
  
- **RISK-003**: Emails duplicados en BD vs archivo pueden causar conflictos
  - **Mitigación**: Validar duplicados antes de transacción atómica
  
- **RISK-004**: Formato de fecha incorrecto en Excel (dd/mm/yyyy vs yyyy-mm-dd)
  - **Mitigación**: Forzar formato ISO 8601 en plantilla y documentación

### Assumptions

- **ASSUMPTION-001**: Usuarios administradores tienen Excel instalado (o compatible)
- **ASSUMPTION-002**: Máximo 200 estudiantes nuevos por carga (en la práctica)
- **ASSUMPTION-003**: Emails son únicos y válidos (validados por Pydantic)
- **ASSUMPTION-004**: No se requiere historial de importaciones (log simple)
- **ASSUMPTION-005**: Contraseñas en Excel son temporales (estudiantes deben cambiar)

## 8. Related Specifications

- [README.md](../README.md#-arquitectura)
- [AGENTS.md](../AGENTS.md)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Openpyxl Documentation](https://openpyxl.readthedocs.io/)
- [FastAPI File Upload](https://fastapi.tiangolo.com/tutorial/request-files/)
