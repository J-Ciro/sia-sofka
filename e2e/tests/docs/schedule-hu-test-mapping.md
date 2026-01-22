# Mapeo de Historias de Usuario - Tests E2E de Horarios y Calendario

Este documento mapea las Historias de Usuario del sistema de horarios y calendario con sus respectivos tests E2E automatizados.

## Fuente de Historias de Usuario
- **Archivo**: `.github/historias-usuario/hu-horarios-calendario.md`
- **Plan de Implementación**: `.github/plan/feature-horarios-calendario-1.md`

## Mapeo HU → Tests E2E

### HU-01: Crear Horario de Clase

| Escenario | Criterio de Aceptación | Test E2E | Estado |
|-----------|------------------------|----------|--------|
| **Escenario 1** | Crear horario exitosamente sin conflictos | `schedules.spec.js` → `HU-01: Crear Horario de Clase` → `Escenario 1: Crear horario exitosamente sin conflictos` | ✅ |
| **Escenario 2** | Validación de hora fin posterior a hora inicio | `schedules.spec.js` → `HU-01: Crear Horario de Clase` → `Escenario 2: Validación de hora fin posterior a hora inicio` | ✅ |
| **Escenario 3** | Validación de duración mínima y máxima | `schedules.spec.js` → `HU-01: Crear Horario de Clase` → `Escenario 3: Validación de duración mínima y máxima` | ✅ |

**Validaciones Cubiertas:**
- ✅ Formulario con campos obligatorios (Materia, Profesor, Salón, Día, Hora Inicio, Hora Fin)
- ✅ Validación de hora fin posterior a hora inicio
- ✅ Validación de duración mínima (30 minutos)
- ✅ Validación de duración máxima (6 horas)
- ✅ Generación de código único para horario
- ✅ Aparición del horario en calendario

---

### HU-02: Validar Conflictos de Salón

| Escenario | Criterio de Aceptación | Test E2E | Estado |
|-----------|------------------------|----------|--------|
| **Escenario 1** | Detectar conflicto de salón | `schedules.spec.js` → `HU-02: Validar Conflictos de Salón` → `Escenario 1: Detectar conflicto de salón` | ✅ |
| **Escenario 2** | Horarios consecutivos sin conflicto | `schedules.spec.js` → `HU-02: Validar Conflictos de Salón` → `Escenario 2: Horarios consecutivos sin conflicto` | ✅ |
| **Escenario 3** | Salones diferentes sin conflicto | `schedules.spec.js` → `HU-02: Validar Conflictos de Salón` → `Escenario 3: Salones diferentes sin conflicto` | ✅ |

**Validaciones Cubiertas:**
- ✅ Detección de solapamiento de horarios en mismo salón
- ✅ Mensaje de error específico con detalles del conflicto
- ✅ Sugerencia de horario conflictivo existente
- ✅ Permitir horarios consecutivos (10:00-12:00 después de 08:00-10:00)
- ✅ Permitir mismo horario en salones diferentes

---

### HU-03: Validar Conflictos de Profesor

| Escenario | Criterio de Aceptación | Test E2E | Estado |
|-----------|------------------------|----------|--------|
| **Escenario 1** | Detectar conflicto de profesor | `schedules.spec.js` → `HU-03: Validar Conflictos de Profesor` → `Escenario 1: Detectar conflicto de profesor` | ✅ |
| **Escenario 2** | Profesor con clases en días diferentes | `schedules.spec.js` → `HU-03: Validar Conflictos de Profesor` → `Escenario 2: Profesor con clases en días diferentes` | ✅ |
| **Escenario 3** | Validación de tiempo de traslado entre salones | `schedules.spec.js` → `HU-03: Validar Conflictos de Profesor` → `Escenario 3: Validación de tiempo de traslado entre salones` | ✅ |

**Validaciones Cubiertas:**
- ✅ Detección de conflicto cuando profesor tiene clases simultáneas
- ✅ Mensaje de error con detalles del horario conflictivo
- ✅ Opción "Ver Horario del Profesor"
- ✅ Permitir clases del mismo profesor en días diferentes
- ✅ Advertencia de tiempo de traslado entre salones lejanos
- ✅ Opciones de confirmar o cancelar asignación con advertencia

---

### HU-04: Editar Horario Existente

| Escenario | Criterio de Aceptación | Test E2E | Estado |
|-----------|------------------------|----------|--------|
| **Escenario 1** | Editar horario sin conflictos | `schedules.spec.js` → `HU-04: Editar Horario Existente` → `Escenario 1: Editar horario sin conflictos` | ✅ |
| **Escenario 2** | Editar horario que genera conflicto | `schedules.spec.js` → `HU-04: Editar Horario Existente` → `Escenario 2: Editar horario que genera conflicto` | ✅ |
| **Escenario 3** | Historial de cambios | `schedules.spec.js` → `HU-04: Editar Horario Existente` → `Escenario 3: Historial de cambios` | ✅ |

**Validaciones Cubiertas:**
- ✅ Edición exitosa de horarios sin conflictos
- ✅ Mensaje "Horario actualizado exitosamente"
- ✅ Actualización del calendario con nuevos horarios
- ✅ Detección de conflictos durante edición
- ✅ Prevención de guardado cuando hay conflictos
- ✅ Historial de cambios con fecha, usuario, campo modificado, valores anterior y nuevo

---

### HU-05: Eliminar Horario

| Escenario | Criterio de Aceptación | Test E2E | Estado |
|-----------|------------------------|----------|--------|
| **Escenario 1** | Eliminar horario sin dependencias | `schedules.spec.js` → `HU-05: Eliminar Horario` → `Escenario 1: Eliminar horario sin dependencias` | ✅ |
| **Escenario 2** | Eliminar horario con dependencias | `schedules.spec.js` → `HU-05: Eliminar Horario` → `Escenario 2: Eliminar horario con dependencias` | ✅ |
| **Escenario 3** | Cancelar eliminación | `schedules.spec.js` → `HU-05: Eliminar Horario` → `Escenario 3: Cancelar eliminación` | ✅ |

**Validaciones Cubiertas:**
- ✅ Modal de confirmación con detalles del horario
- ✅ Eliminación exitosa sin dependencias
- ✅ Advertencia cuando existen sesiones de asistencia
- ✅ Opciones "Eliminar De Todas Formas" y "Cancelar"
- ✅ Cancelación de eliminación mantiene horario intacto

---

### HU-06: Visualizar Calendario Semanal

| Escenario | Criterio de Aceptación | Test E2E | Estado |
|-----------|------------------------|----------|--------|
| **Escenario 1** | Ver calendario con horarios | `schedules.spec.js` → `HU-06: Visualizar Calendario Semanal` → `Escenario 1: Ver calendario con horarios` | ✅ |
| **Escenario 2** | Clases superpuestas visualmente distinguibles | `schedules.spec.js` → `HU-06: Visualizar Calendario Semanal` → `Escenario 2: Clases superpuestas visualmente distinguibles` | ✅ |
| **Escenario 3** | Navegación entre semanas | `schedules.spec.js` → `HU-06: Visualizar Calendario Semanal` → `Escenario 3: Navegación entre semanas` | ✅ |

**Validaciones Cubiertas:**
- ✅ Calendario semanal con columnas Lunes-Sábado
- ✅ Filas representando horas (07:00-22:00)
- ✅ Bloques visuales con información completa (Materia, Profesor, Salón, Hora)
- ✅ Colores diferentes por materia
- ✅ Bloques en conflicto con borde rojo y ícono de advertencia
- ✅ Tooltips explicando conflictos
- ✅ Navegación "Semana Anterior", "Semana Siguiente", "Hoy"
- ✅ Rango de fechas visible

---

### HU-07: Filtrar Horarios en Calendario

| Escenario | Criterio de Aceptación | Test E2E | Estado |
|-----------|------------------------|----------|--------|
| **Escenario 1** | Filtrar por profesor | `schedules.spec.js` → `HU-07: Filtrar Horarios en Calendario` → `Escenario 1: Filtrar por profesor` | ✅ |
| **Escenario 2** | Filtrar por salón | `schedules.spec.js` → `HU-07: Filtrar Horarios en Calendario` → `Escenario 2: Filtrar por salón` | ✅ |
| **Escenario 3** | Filtrar por materia | `schedules.spec.js` → `HU-07: Filtrar Horarios en Calendario` → `Escenario 3: Filtrar por materia` | ✅ |
| **Escenario 4** | Combinar múltiples filtros | `schedules.spec.js` → `HU-07: Filtrar Horarios en Calendario` → `Escenario 4: Combinar múltiples filtros` | ✅ |
| **Escenario 5** | Limpiar todos los filtros | `schedules.spec.js` → `HU-07: Filtrar Horarios en Calendario` → `Escenario 5: Limpiar todos los filtros` | ✅ |

**Validaciones Cubiertas:**
- ✅ Filtro por profesor con actualización en tiempo real
- ✅ Contador "Mostrando X de Y horarios"
- ✅ Filtro por salón mostrando solo clases del salón seleccionado
- ✅ Filtro por materia con selección múltiple via checkboxes
- ✅ Combinación de múltiples filtros (Profesor + Día)
- ✅ Resumen de resultados filtrados
- ✅ Botón "Limpiar Filtros" restaura vista completa

---

### HU-08: Ver Detalle de Horario desde Calendario

| Escenario | Criterio de Aceptación | Test E2E | Estado |
|-----------|------------------------|----------|--------|
| **Escenario 1** | Ver modal de detalle | `schedules.spec.js` → `HU-08: Ver Detalle de Horario desde Calendario` → `Escenario 1: Ver modal de detalle` | ✅ |
| **Escenario 2** | Acciones rápidas desde el modal | `schedules.spec.js` → `HU-08: Ver Detalle de Horario desde Calendario` → `Escenario 2: Acciones rápidas desde el modal` | ✅ |

**Validaciones Cubiertas:**
- ✅ Modal con información detallada (Código, Materia, Profesor, Email, Salón, Día, Hora, Duración, Estudiantes Inscritos)
- ✅ Botones de acción: "Editar Horario", "Ver Asistencias", "Cerrar"
- ✅ Redirección a sección de asistencia con horario pre-seleccionado

---

### HU-09: Exportar Horarios a PDF

| Escenario | Criterio de Aceptación | Test E2E | Estado |
|-----------|------------------------|----------|--------|
| **Escenario 1** | Exportar calendario semanal completo | `schedules.spec.js` → `HU-09: Exportar Horarios a PDF` → `Escenario 1: Exportar calendario semanal completo` | ✅ |
| **Escenario 2** | Exportar horarios de un profesor | `schedules.spec.js` → `HU-09: Exportar Horarios a PDF` → `Escenario 2: Exportar horarios de un profesor` | ✅ |

**Validaciones Cubiertas:**
- ✅ Opciones de exportación (Vista: Semanal/Mensual, Orientación: Horizontal/Vertical, Incluir: Todos/Solo filtrados)
- ✅ Descarga de PDF con nombre "horarios_semana_XX_2026.pdf"
- ✅ Exportación de horarios filtrados por profesor
- ✅ PDF incluye nombre del profesor en encabezado cuando está filtrado

---

### HU-10: Notificar Cambios de Horario

| Escenario | Criterio de Aceptación | Test E2E | Estado |
|-----------|------------------------|----------|--------|
| **Escenario 1** | Notificación por edición de horario | `schedules.spec.js` → `HU-10: Notificar Cambios de Horario` → `Escenario 1: Notificación por edición de horario` | ✅ |
| **Escenario 2** | Notificación por eliminación de horario | `schedules.spec.js` → `HU-10: Notificar Cambios de Horario` → `Escenario 2: Notificación por eliminación de horario` | ✅ |
| **Escenario 3** | Centro de notificaciones | `schedules.spec.js` → `HU-10: Notificar Cambios de Horario` → `Escenario 3: Centro de notificaciones` | ✅ |

**Validaciones Cubiertas:**
- ✅ Notificación en sistema cuando horario es modificado
- ✅ Email con detalles del cambio
- ✅ Botón "Ver Horario Actualizado"
- ✅ Notificación de cancelación de clase
- ✅ Fecha y hora de cancelación
- ✅ Centro de notificaciones con ícono de campana
- ✅ Indicador visual para notificaciones no leídas
- ✅ Función "Marcar todas como leídas"

---

## 🔴 COBERTURA EXHAUSTIVA - NO SOLO HAPPY PATH

### Casos Negativos y Edge Cases Completos

**Los tests van MÁS ALLÁ del happy path** - Cobertura exhaustiva de **71 tests** incluyendo:

#### 🔴 Casos Negativos por Historia de Usuario

**HU-01: Crear Horario de Clase** (9 tests)
- ✅ **Happy Path**: Creación exitosa sin conflictos
- ❌ **Casos Negativos**: 
  - Hora fin antes de hora inicio
  - Duración menor a 30 minutos / mayor a 6 horas
  - Duración cero (inicio = fin)
  - Campos obligatorios faltantes
  - Inyección XSS y SQL injection
  - Campos con longitud excesiva
  - Doble envío (double submit prevention)
  - Formato de hora inválido

**HU-02: Validar Conflictos de Salón** (6 tests)
- ✅ **Happy Path**: Detección correcta de conflictos
- ❌ **Casos Negativos**:
  - Triple conflicto (salón + profesor + horario)
  - Solapamiento mínimo (1 minuto)
  - Conflicto en horario límite (23:59)

**HU-03: Validar Conflictos de Profesor** (6 tests)
- ✅ **Happy Path**: Detección de conflictos de profesor
- ❌ **Casos Negativos**:
  - Profesor con múltiples materias simultáneas
  - Carga horaria excesiva (>8 horas diarias)
  - Días consecutivos sin descanso

**HU-07: Filtrar Horarios** (9 tests)
- ✅ **Happy Path**: Filtros funcionando correctamente
- ❌ **Casos Negativos**:
  - Filtros con resultados vacíos
  - Caracteres especiales en filtros
  - Filtros contradictorios
  - Performance con datasets grandes

#### 🔴 Casos de Error de Sistema (25 tests)

**Errores de Red y Conectividad**
- ❌ Error de conexión durante creación
- ❌ Timeout durante carga de calendario
- ❌ Error 500 del servidor durante eliminación
- ❌ Error 401 - Sesión expirada
- ❌ Pérdida de conexión intermitente

**Validaciones de Campos**
- ❌ Formulario completamente vacío
- ❌ Cada campo obligatorio faltante individualmente
- ❌ Formato de datos inválido (25:70 como hora)
- ❌ Rangos de valores fuera de límites

#### 🔴 Casos de Seguridad (8 tests)

**Inyección y Ataques**
- ❌ Inyección XSS: `<script>alert("XSS")</script>`
- ❌ Inyección SQL: `'; DROP TABLE schedules; --`
- ❌ Manipulación de datos en cliente (JavaScript)
- ❌ Acceso no autorizado por rol

**Control de Acceso**
- ❌ Usuario estudiante intentando crear horarios
- ❌ Sesión expirada durante operación
- ❌ Permisos insuficientes para operaciones

#### 🔴 Casos de Performance y Límites (6 tests)

**Boundary Testing**
- ❌ Horario límite superior (23:59)
- ❌ Horario límite inferior (00:00)
- ❌ Duración mínima exacta (30 min)
- ❌ Duración máxima exacta (6 horas)

**Stress Testing**
- ❌ Calendario con 100+ horarios
- ❌ Filtros en datasets grandes
- ❌ Navegación extensiva (memory leaks)

#### 🔴 Casos de Usabilidad Extrema (4 tests)

**Condiciones Adversas**
- ❌ JavaScript deshabilitado/limitado
- ❌ Resolución extremadamente pequeña (320x568)
- ❌ Navegación solo con teclado (accesibilidad)
- ❌ Conexión lenta/intermitente

#### 🔴 Casos de Recuperación y Resilencia (4 tests)

**Error Recovery**
- ❌ Recuperación después de múltiples errores consecutivos
- ❌ Estado del formulario tras error de red
- ❌ Reintentos automáticos
- ❌ Degradación elegante del sistema

### 📊 Métricas de Cobertura Detallada

| Categoría | Happy Path | Casos Negativos | Edge Cases | Total |
|-----------|------------|-----------------|------------|-------|
| **HU-01: Crear Horario** | 3 | 6 | 0 | 9 |
| **HU-02: Conflictos Salón** | 3 | 3 | 0 | 6 |
| **HU-03: Conflictos Profesor** | 3 | 3 | 0 | 6 |
| **HU-04: Editar Horario** | 3 | 0 | 0 | 3 |
| **HU-05: Eliminar Horario** | 3 | 0 | 0 | 3 |
| **HU-06: Calendario Visual** | 3 | 0 | 0 | 3 |
| **HU-07: Filtros** | 5 | 4 | 0 | 9 |
| **HU-08: Ver Detalle** | 2 | 0 | 0 | 2 |
| **HU-09: Exportar PDF** | 2 | 0 | 0 | 2 |
| **HU-10: Notificaciones** | 3 | 0 | 0 | 3 |
| **🔴 Edge Cases Críticos** | 0 | 0 | 25 | 25 |
| **TOTAL** | **30** | **16** | **25** | **71** |

### 🎯 Distribución de Cobertura

- ✅ **Happy Path**: 30 tests (42%)
- ❌ **Casos Negativos**: 16 tests (23%)
- 🔄 **Edge Cases**: 25 tests (35%)
- 🛡️ **Seguridad**: 8 tests (11%)
- ⚡ **Performance**: 6 tests (8%)
- 🔧 **Recuperación**: 4 tests (6%)

### 🚨 Casos Críticos que DEBEN Fallar

**Validaciones de Seguridad**
```javascript
// DEBE rechazar inyección XSS
materia: '<script>alert("XSS")</script>'

// DEBE rechazar inyección SQL  
profesor: "'; DROP TABLE schedules; --"

// DEBE prevenir acceso no autorizado
estudianteePage.goto('/schedules') // DEBE fallar
```

**Validaciones de Negocio**
```javascript
// DEBE rechazar horarios inválidos
horaInicio: '15:00', horaFin: '14:00' // DEBE fallar

// DEBE detectar conflictos mínimos
solapamiento: '1 minuto' // DEBE fallar

// DEBE prevenir doble envío
submitButton.click(); submitButton.click(); // DEBE crear solo 1
```

**Validaciones de Sistema**
```javascript
// DEBE manejar errores de red
route.abort('failed') // DEBE mostrar error apropiado

// DEBE manejar timeouts
setTimeout(10000) // DEBE mostrar loading/timeout

// DEBE preservar estado tras error
formData.persist() // DEBE mantener datos tras error
```

---

## Cobertura de Métricas de Éxito

| Métrica | Validación en Tests | Estado |
|---------|-------------------|--------|
| **Tiempo de creación de horario < 30 segundos** | Timeout de 10 segundos en formularios | ✅ |
| **Detección de conflictos 100% precisión** | Tests específicos para cada tipo de conflicto | ✅ |
| **Tiempo de carga del calendario < 2 segundos** | Performance test con timeout de 5 segundos | ✅ |
| **Tasa de error en creación < 1%** | Validación de mensajes de éxito/error | ✅ |

---

## Archivos de Test

### Principales
- **`e2e/tests/e2e/schedules.spec.js`**: Tests principales de todas las HU
- **`e2e/tests/pages/SchedulePage.js`**: Page Object Model para horarios y calendario

### Fixtures y Helpers
- **`e2e/tests/fixtures/auth.js`**: Autenticación para diferentes roles
- **`e2e/tests/helpers/dateHelpers.js`**: Utilidades para manejo de fechas (reutilizado)

---

## Patrón de Implementación TDD

### 1. Red Phase (Tests Failing)
```bash
cd e2e
npm run test:e2e -- schedules.spec.js
```

### 2. Green Phase (Implement Features)
- Implementar endpoints backend en `backend/app/api/v1/endpoints/schedules.py`
- Implementar componentes frontend en `frontend/src/components/schedule/`
- Implementar validaciones de conflictos en `backend/app/services/schedule_service.py`

### 3. Refactor Phase (Optimize)
- Optimizar queries de detección de conflictos
- Mejorar performance del calendario
- Refinar UX de notificaciones

---

## Comandos de Ejecución

### Ejecutar todos los tests de horarios
```bash
cd e2e
npm run test:e2e -- schedules.spec.js
```

### Ejecutar tests específicos por HU
```bash
# HU-01: Crear Horario
npm run test:e2e -- schedules.spec.js -g "HU-01: Crear Horario de Clase"

# HU-02: Conflictos de Salón
npm run test:e2e -- schedules.spec.js -g "HU-02: Validar Conflictos de Salón"

# HU-06: Calendario Visual
npm run test:e2e -- schedules.spec.js -g "HU-06: Visualizar Calendario Semanal"
```

### Ejecutar con UI para debugging
```bash
npm run test:e2e:ui -- schedules.spec.js
```

### Generar reporte
```bash
npm run test:e2e:report
```

---

## Notas de Implementación

### Dependencias Frontend
- **react-big-calendar**: Para el componente de calendario visual
- **date-fns**: Para manejo de fechas y horarios
- **Tailwind CSS**: Para estilos y colores diferenciados

### Dependencias Backend
- **PostgreSQL**: Operadores de intervalo para detección de solapamientos
- **SQLAlchemy**: Queries complejas de conflictos
- **Alembic**: Migraciones para modelos Schedule y Classroom

### Consideraciones de Performance
- Índices en `(aula_id, dia_semana, hora_inicio)`
- Paginación en calendario mensual
- Lazy loading de eventos distantes

### Consideraciones de UX
- Colores consistentes por materia usando hash de ID
- Tooltips informativos en conflictos
- Feedback visual inmediato en operaciones
- Confirmaciones para acciones destructivas

---

## Estado de Implementación

- ✅ **Tests E2E**: Completos y listos para ejecución
- ⏳ **Backend**: En desarrollo según plan de implementación
- ⏳ **Frontend**: En desarrollo según plan de implementación
- ⏳ **Integración**: Pendiente de completar backend y frontend

**Próximos Pasos:**
1. Ejecutar tests para identificar funcionalidades faltantes
2. Implementar endpoints backend según fallos de tests
3. Implementar componentes frontend según fallos de tests
4. Iterar hasta que todos los tests pasen (Green Phase)
5. Refactorizar y optimizar (Refactor Phase)