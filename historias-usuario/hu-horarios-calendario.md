---
title: Historias de Usuario - Sistema de Horarios y Calendario
version: 1.0
date_created: 2026-01-19
last_updated: 2026-01-19
---

# Historias de Usuario - Sistema de Horarios y Calendario

## Epic: Sistema de Gestión de Horarios y Visualización de Calendario

**Como** administrador y profesor del sistema académico,
**Quiero** gestionar horarios de clases con validación de conflictos y visualizarlos en un calendario interactivo,
**Para** organizar eficientemente los espacios, profesores y materias sin colisiones.

---

## HU-01: Crear Horario de Clase

### Historia de Usuario
**Como** administrador,
**Quiero** crear un horario para una clase asignando materia, profesor, salón, día y hora,
**Para** organizar el calendario académico del período.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Crear horario exitosamente sin conflictos
```gherkin
Given que estoy autenticado como administrador
When accedo a "Gestión de Horarios"
And presiono el botón "Crear Nuevo Horario"
Then debo ver un formulario con los campos:
  | Campo | Tipo | Obligatorio |
  | Materia | Select | Sí |
  | Profesor | Select | Sí |
  | Salón | Text | Sí |
  | Día de la Semana | Select | Sí |
  | Hora Inicio | Time | Sí |
  | Hora Fin | Time | Sí |
When completo:
  | Campo | Valor |
  | Materia | Matemáticas Avanzadas |
  | Profesor | Dr. Juan Pérez |
  | Salón | Aula 301 |
  | Día de la Semana | Lunes |
  | Hora Inicio | 08:00 |
  | Hora Fin | 10:00 |
And presiono "Crear Horario"
Then debo ver el mensaje "Horario creado exitosamente"
And el horario debe aparecer en el calendario
And el sistema debe generar un código único para el horario
```

#### Escenario 2: Validación de hora fin posterior a hora inicio
```gherkin
Given que estoy creando un horario
When ingreso:
  | Hora Inicio | 10:00 |
  | Hora Fin | 08:00 |
Then debo ver el error: "La hora de fin debe ser posterior a la hora de inicio"
And el botón "Crear Horario" debe estar deshabilitado
```

#### Escenario 3: Validación de duración mínima y máxima
```gherkin
Given que estoy creando un horario
When ingreso una duración menor a 30 minutos
Then debo ver el error: "La clase debe durar al menos 30 minutos"
When ingreso una duración mayor a 6 horas
Then debo ver el error: "La clase no puede durar más de 6 horas"
```

---

## HU-02: Validar Conflictos de Salón

### Historia de Usuario
**Como** administrador,
**Quiero** que el sistema valide automáticamente si un salón ya está ocupado,
**Para** evitar asignar el mismo espacio físico a dos clases simultáneas.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Detectar conflicto de salón
```gherkin
Given que existe un horario:
  | Salón | Día | Hora Inicio | Hora Fin |
  | Aula 301 | Lunes | 08:00 | 10:00 |
When intento crear otro horario con:
  | Salón | Día | Hora Inicio | Hora Fin |
  | Aula 301 | Lunes | 09:00 | 11:00 |
Then debo ver un error de conflicto: "El Aula 301 ya está ocupada el Lunes de 08:00 a 10:00"
And debo ver sugerencia: "Horario conflictivo: Matemáticas Avanzadas con Dr. Juan Pérez"
And el formulario debe marcarse como inválido
```

#### Escenario 2: Horarios consecutivos sin conflicto
```gherkin
Given que existe un horario:
  | Salón | Día | Hora Inicio | Hora Fin |
  | Aula 301 | Lunes | 08:00 | 10:00 |
When intento crear otro horario con:
  | Salón | Día | Hora Inicio | Hora Fin |
  | Aula 301 | Lunes | 10:00 | 12:00 |
Then el sistema NO debe mostrar error de conflicto
And debo poder crear el horario exitosamente
```

#### Escenario 3: Salones diferentes sin conflicto
```gherkin
Given que existe un horario:
  | Salón | Día | Hora Inicio | Hora Fin |
  | Aula 301 | Lunes | 08:00 | 10:00 |
When intento crear otro horario con:
  | Salón | Día | Hora Inicio | Hora Fin |
  | Aula 302 | Lunes | 08:00 | 10:00 |
Then el sistema NO debe mostrar error
And ambos horarios deben coexistir sin problemas
```

---

## HU-03: Validar Conflictos de Profesor

### Historia de Usuario
**Como** administrador,
**Quiero** que el sistema valide si un profesor ya tiene clase asignada en el mismo horario,
**Para** evitar asignar al mismo profesor en dos lugares simultáneamente.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Detectar conflicto de profesor
```gherkin
Given que el "Dr. Juan Pérez" tiene asignado:
  | Materia | Día | Hora Inicio | Hora Fin | Salón |
  | Matemáticas | Lunes | 08:00 | 10:00 | Aula 301 |
When intento asignarle otra clase:
  | Materia | Día | Hora Inicio | Hora Fin | Salón |
  | Física | Lunes | 09:30 | 11:30 | Aula 205 |
Then debo ver el error: "Dr. Juan Pérez ya tiene clase el Lunes de 08:00 a 10:00"
And debo ver el detalle del horario conflictivo
And debo tener la opción "Ver Horario del Profesor"
```

#### Escenario 2: Profesor con clases en días diferentes
```gherkin
Given que el "Dr. Juan Pérez" tiene clase el Lunes 08:00-10:00
When intento asignarle clase el Martes 08:00-10:00
Then NO debe haber conflicto
And el horario debe crearse exitosamente
```

#### Escenario 3: Validación de tiempo de traslado entre salones
```gherkin
Given que el "Dr. Juan Pérez" tiene clase:
  | Día | Hora Fin | Salón |
  | Lunes | 10:00 | Aula 301 |
When intento asignarle otra clase:
  | Día | Hora Inicio | Salón |
  | Lunes | 10:00 | Aula 501 |
Then debo ver una advertencia: "No hay tiempo de traslado entre salones"
And debo poder confirmar o cancelar la asignación
```

---

## HU-04: Editar Horario Existente

### Historia de Usuario
**Como** administrador,
**Quiero** modificar un horario existente,
**Para** ajustar cambios en la programación académica.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Editar horario sin conflictos
```gherkin
Given que existe un horario:
  | ID | Materia | Profesor | Día | Hora Inicio | Hora Fin | Salón |
  | H001 | Matemáticas | Dr. Pérez | Lunes | 08:00 | 10:00 | Aula 301 |
When hago clic en el botón "Editar" del horario H001
And cambio:
  | Campo | Nuevo Valor |
  | Hora Inicio | 09:00 |
  | Hora Fin | 11:00 |
And presiono "Guardar Cambios"
Then debo ver el mensaje "Horario actualizado exitosamente"
And el calendario debe reflejar los nuevos horarios
```

#### Escenario 2: Editar horario que genera conflicto
```gherkin
Given que existe un horario H001 en Aula 301 Lunes 08:00-10:00
And existe otro horario H002 en Aula 301 Lunes 11:00-13:00
When intento editar H001 cambiando:
  | Hora Fin | 12:00 |
Then debo ver el error: "Este cambio genera conflicto con otro horario"
And debo ver los detalles del horario conflictivo (H002)
And los cambios NO deben guardarse
```

#### Escenario 3: Historial de cambios
```gherkin
Given que he editado un horario
When accedo al detalle del horario
And presiono "Ver Historial de Cambios"
Then debo ver una tabla con:
  | Fecha | Usuario | Campo Modificado | Valor Anterior | Valor Nuevo |
  | 2026-01-19 14:30 | admin@sofka.com | Hora Inicio | 08:00 | 09:00 |
And el historial debe estar ordenado por fecha descendente
```

---

## HU-05: Eliminar Horario

### Historia de Usuario
**Como** administrador,
**Quiero** eliminar un horario,
**Para** remover clases canceladas o corregir errores.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Eliminar horario sin dependencias
```gherkin
Given que existe un horario H001 sin sesiones de asistencia registradas
When hago clic en el botón "Eliminar" del horario H001
Then debo ver un modal de confirmación: "¿Está seguro de eliminar este horario?"
And debo ver los detalles del horario a eliminar
When confirmo la eliminación
Then debo ver el mensaje "Horario eliminado exitosamente"
And el horario debe desaparecer del calendario
```

#### Escenario 2: Eliminar horario con dependencias
```gherkin
Given que existe un horario H001
And existen 5 sesiones de asistencia registradas para este horario
When intento eliminar el horario H001
Then debo ver una advertencia: "Este horario tiene 5 sesiones de asistencia registradas"
And debo tener las opciones:
  - "Eliminar De Todas Formas" (elimina también las sesiones)
  - "Cancelar"
```

#### Escenario 3: Cancelar eliminación
```gherkin
Given que estoy en el modal de confirmación de eliminación
When presiono el botón "Cancelar"
Then el modal debe cerrarse
And el horario NO debe eliminarse
And debo permanecer en la vista de horarios
```

---

## HU-06: Visualizar Calendario Semanal

### Historia de Usuario
**Como** profesor y administrador,
**Quiero** ver todos los horarios en un calendario visual semanal,
**Para** tener una vista clara de la programación de clases.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Ver calendario con horarios
```gherkin
Given que existen múltiples horarios creados
When accedo a la sección "Calendario de Clases"
Then debo ver un calendario semanal con:
  - Columnas para cada día (Lunes a Sábado)
  - Filas representando horas (07:00 - 22:00)
  - Bloques visuales para cada clase
And cada bloque debe mostrar:
  | Información | Ejemplo |
  | Materia | Matemáticas Avanzadas |
  | Profesor | Dr. Juan Pérez |
  | Salón | Aula 301 |
  | Hora | 08:00 - 10:00 |
And los bloques deben tener colores diferentes según la materia
```

#### Escenario 2: Clases superpuestas visualmente distinguibles
```gherkin
Given que hay un conflicto no resuelto (dos horarios superpuestos)
When visualizo el calendario
Then los bloques en conflicto deben mostrarse con:
  - Borde rojo grueso
  - Ícono de advertencia ⚠️
  - Tooltip explicando el conflicto
```

#### Escenario 3: Navegación entre semanas
```gherkin
Given que estoy viendo la semana actual
When presiono el botón "Semana Anterior"
Then debo ver los horarios de la semana anterior
And debo ver el rango de fechas: "13 Ene - 19 Ene 2026"
When presiono "Semana Siguiente"
Then debo avanzar a la siguiente semana
When presiono "Hoy"
Then debo volver a la semana actual
```

---

## HU-07: Filtrar Horarios en Calendario

### Historia de Usuario
**Como** usuario del sistema,
**Quiero** filtrar los horarios mostrados en el calendario,
**Para** enfocarme solo en la información relevante.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Filtrar por profesor
```gherkin
Given que el calendario muestra horarios de todos los profesores
When selecciono el filtro "Profesor: Dr. Juan Pérez"
Then debo ver solo los horarios asignados al Dr. Juan Pérez
And los demás horarios deben ocultarse
And debo ver un contador: "Mostrando 8 de 45 horarios"
```

#### Escenario 2: Filtrar por salón
```gherkin
Given que estoy viendo el calendario completo
When selecciono el filtro "Salón: Aula 301"
Then debo ver solo las clases que ocurren en Aula 301
And el calendario debe actualizarse en tiempo real
```

#### Escenario 3: Filtrar por materia
```gherkin
Given que tengo múltiples materias en el calendario
When selecciono el filtro "Materia: Matemáticas Avanzadas"
Then debo ver solo las clases de Matemáticas Avanzadas
And debo poder seleccionar múltiples materias con checkboxes
```

#### Escenario 4: Combinar múltiples filtros
```gherkin
Given que estoy viendo el calendario
When aplico los filtros:
  | Tipo | Valor |
  | Profesor | Dr. Juan Pérez |
  | Día | Lunes |
Then debo ver solo las clases del Dr. Juan Pérez que ocurren los Lunes
And debo ver un resumen: "2 clases encontradas"
```

#### Escenario 5: Limpiar todos los filtros
```gherkin
Given que tengo múltiples filtros aplicados
When presiono el botón "Limpiar Filtros"
Then todos los filtros deben removerse
And debo ver el calendario completo nuevamente
```

---

## HU-08: Ver Detalle de Horario desde Calendario

### Historia de Usuario
**Como** usuario del sistema,
**Quiero** hacer clic en un bloque del calendario para ver el detalle completo,
**Para** acceder rápidamente a toda la información de la clase.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Ver modal de detalle
```gherkin
Given que estoy viendo el calendario semanal
When hago clic en un bloque de clase
Then debo ver un modal con información detallada:
  | Campo | Ejemplo |
  | Código | HOR-001 |
  | Materia | Matemáticas Avanzadas |
  | Código Materia | MAT-301 |
  | Profesor | Dr. Juan Pérez |
  | Email Profesor | juan.perez@sofka.edu |
  | Salón | Aula 301 |
  | Día | Lunes |
  | Hora | 08:00 - 10:00 |
  | Duración | 2 horas |
  | Estudiantes Inscritos | 25 |
And debo ver botones de acción:
  - "Editar Horario"
  - "Ver Asistencias"
  - "Cerrar"
```

#### Escenario 2: Acciones rápidas desde el modal
```gherkin
Given que estoy viendo el modal de detalle de un horario
When presiono el botón "Ver Asistencias"
Then debo ser redirigido a la sección de asistencia
And debe pre-seleccionarse este horario
```

---

## HU-09: Exportar Horarios a PDF

### Historia de Usuario
**Como** administrador,
**Quiero** exportar los horarios a un archivo PDF,
**Para** imprimirlos y distribuirlos físicamente.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Exportar calendario semanal completo
```gherkin
Given que estoy viendo el calendario semanal
When presiono el botón "Exportar a PDF"
Then debo ver opciones de exportación:
  - Vista: Semanal / Mensual
  - Orientación: Horizontal / Vertical
  - Incluir: Todos / Solo filtrados
When selecciono:
  | Opción | Valor |
  | Vista | Semanal |
  | Orientación | Horizontal |
  | Incluir | Todos |
And confirmo la exportación
Then debo descargar un PDF con:
  - Nombre: "horarios_semana_20_2026.pdf"
  - Calendario visual similar a la vista web
  - Leyenda de colores por materia
  - Fecha de generación
```

#### Escenario 2: Exportar horarios de un profesor
```gherkin
Given que he aplicado el filtro "Profesor: Dr. Juan Pérez"
When exporto a PDF seleccionando "Solo filtrados"
Then el PDF debe contener únicamente los horarios del Dr. Juan Pérez
And debe incluir el nombre del profesor en el encabezado
```

---

## HU-10: Notificar Cambios de Horario

### Historia de Usuario
**Como** profesor,
**Quiero** recibir notificaciones cuando mis horarios sean modificados,
**Para** estar informado de cambios en mi agenda.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Notificación por edición de horario
```gherkin
Given que soy el profesor "Dr. Juan Pérez"
And tengo asignado un horario H001
When un administrador edita mi horario H001 cambiando:
  | Campo | Valor Anterior | Valor Nuevo |
  | Hora Inicio | 08:00 | 09:00 |
Then debo recibir una notificación en el sistema: "Su horario de Matemáticas Avanzadas ha sido modificado"
And debo recibir un email con los detalles del cambio
And la notificación debe incluir un botón "Ver Horario Actualizado"
```

#### Escenario 2: Notificación por eliminación de horario
```gherkin
Given que tengo un horario asignado
When un administrador elimina mi horario
Then debo recibir una notificación: "Su clase de Matemáticas Avanzadas (Lunes 08:00) ha sido cancelada"
And debo ver la fecha y hora de la cancelación
```

#### Escenario 3: Centro de notificaciones
```gherkin
Given que he recibido 3 notificaciones de cambios de horario
When hago clic en el ícono de campana 🔔
Then debo ver una lista de mis notificaciones
And las no leídas deben tener un indicador visual
When hago clic en "Marcar todas como leídas"
Then todas las notificaciones deben cambiar a estado "leída"
```

---

## Resumen de Priorización (MoSCoW)

### Must Have (MVP)
- HU-01: Crear Horario de Clase
- HU-02: Validar Conflictos de Salón
- HU-03: Validar Conflictos de Profesor
- HU-04: Editar Horario Existente
- HU-06: Visualizar Calendario Semanal

### Should Have
- HU-05: Eliminar Horario
- HU-07: Filtrar Horarios en Calendario
- HU-08: Ver Detalle de Horario desde Calendario

### Could Have
- HU-09: Exportar Horarios a PDF
- HU-10: Notificar Cambios de Horario

---

## Métricas de Éxito

- **Tiempo de creación de horario:** < 30 segundos
- **Detección de conflictos:** 100% de precisión
- **Tiempo de carga del calendario:** < 2 segundos
- **Tasa de error en creación de horarios:** < 1%
- **Satisfacción de usuarios:** > 4.3/5 estrellas

---

## Notas para Implementación TDD

1. **Orden de implementación:**
   - HU-01 (backend: modelo Schedule, validaciones básicas)
   - HU-02 y HU-03 (lógica de detección de conflictos)
   - HU-06 (frontend: integración react-big-calendar)
   - HU-04 y HU-05 (operaciones CRUD)
   - HU-07, HU-08, HU-09, HU-10 (features avanzadas)

2. **Tests prioritarios:**
   - Unit: Lógica de detección de conflictos (sala y profesor)
   - Unit: Validación de rangos de tiempo
   - Integration: POST /api/v1/schedules con conflictos
   - Integration: GET /api/v1/schedules con filtros
   - E2E: Crear horario, detectar conflicto, resolver

3. **Edge cases críticos:**
   - Horarios a medianoche (23:59 - 00:30)
   - Cambios de horario de verano (si aplica)
   - Clases de múltiples días (Lunes y Miércoles)
   - Profesores con más de 8 horas de clase al día
   - Salones con nombres similares (Aula 301 vs Aula 301A)
