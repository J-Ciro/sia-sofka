---
title: Historias de Usuario - Sistema de Asistencia Manual
version: 1.0
date_created: 2026-01-19
last_updated: 2026-01-19
---

# Historias de Usuario - Sistema de Asistencia Manual

## Epic: Sistema de Registro de Asistencia Manual

**Como** profesor del sistema académico,
**Quiero** registrar la asistencia de mis estudiantes de forma manual y eficiente,
**Para** llevar un control preciso de la asistencia de cada clase y generar reportes estadísticos.

---

## HU-01: Crear Sesión de Asistencia

### Historia de Usuario
**Como** profesor,
**Quiero** crear una sesión de asistencia para una de mis clases,
**Para** registrar quiénes asistieron en una fecha específica.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Crear sesión exitosamente
```gherkin
Given que estoy autenticado como profesor
And tengo asignada la materia "Matemáticas Avanzadas"
And la materia tiene 15 estudiantes inscritos
When accedo a la sección "Asistencia"
And selecciono la materia "Matemáticas Avanzadas"
And presiono el botón "Crear Sesión de Asistencia"
Then debo ver un formulario con los siguientes campos:
  | Campo | Tipo | Obligatorio |
  | Fecha | Date | Sí |
  | Hora Inicio | Time | Sí |
  | Hora Fin | Time | Sí |
  | Descripción | Text | No |
When completo:
  | Campo | Valor |
  | Fecha | 2026-01-19 |
  | Hora Inicio | 08:00 |
  | Hora Fin | 10:00 |
  | Descripción | Clase de Cálculo Diferencial |
And presiono "Crear Sesión"
Then debo ver el mensaje "Sesión creada exitosamente"
And debo ver la lista de estudiantes con estado "Presente" por defecto
And cada estudiante debe tener su código institucional y nombre completo
```

#### Escenario 2: Validación de fecha futura
```gherkin
Given que estoy creando una sesión de asistencia
When selecciono una fecha posterior a hoy
Then debo ver el mensaje de error: "No se puede crear asistencia para fechas futuras"
And el botón "Crear Sesión" debe estar deshabilitado
```

#### Escenario 3: Validación de hora de fin antes de hora inicio
```gherkin
Given que estoy creando una sesión de asistencia
When selecciono:
  | Campo | Valor |
  | Hora Inicio | 10:00 |
  | Hora Fin | 08:00 |
Then debo ver el mensaje: "La hora de fin debe ser posterior a la hora de inicio"
And el formulario debe marcarse como inválido
```

#### Escenario 4: Sesión duplicada en el mismo día
```gherkin
Given que ya existe una sesión de asistencia para "Matemáticas Avanzadas" el 2026-01-19
When intento crear otra sesión para la misma materia y fecha
Then debo ver un mensaje de advertencia: "Ya existe una sesión para esta materia en esta fecha"
And debo tener la opción de "Ver Sesión Existente" o "Crear De Todas Formas"
```

---

## HU-02: Marcar Asistencia con Botones Masivos

### Historia de Usuario
**Como** profesor,
**Quiero** marcar la asistencia de todos los estudiantes con un solo botón,
**Para** ahorrar tiempo cuando la mayoría tiene el mismo estado.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Marcar todos como presente
```gherkin
Given que he creado una sesión de asistencia con 15 estudiantes
And todos los estudiantes tienen estado "Presente" por defecto
When presiono el botón "Marcar Todos Presentes"
Then todos los 15 estudiantes deben tener estado "Presente"
And debo ver un contador: "15 Presentes, 0 Ausentes, 0 Tardanzas"
And el botón debe mostrar feedback visual de éxito
```

#### Escenario 2: Marcar todos como ausente
```gherkin
Given que tengo una sesión con estudiantes en diferentes estados:
  | Estado | Cantidad |
  | Presente | 10 |
  | Ausente | 3 |
  | Tardanza | 2 |
When presiono el botón "Marcar Todos Ausentes"
Then todos los 15 estudiantes deben cambiar a estado "Ausente"
And debo ver el contador: "0 Presentes, 15 Ausentes, 0 Tardanzas"
And debo ver un modal de confirmación: "¿Está seguro de marcar a todos como ausentes?"
```

#### Escenario 3: Marcar todos con tardanza
```gherkin
Given que tengo una sesión de asistencia activa
When presiono el botón "Marcar Todos con Tardanza"
Then todos los estudiantes deben cambiar a estado "Tardanza"
And debo ver el contador: "0 Presentes, 0 Ausentes, 15 Tardanzas"
And debo ver la confirmación: "Se han marcado 15 estudiantes con tardanza"
```

#### Escenario 4: Deshacer acción masiva
```gherkin
Given que acabo de ejecutar "Marcar Todos Ausentes"
And el cambio se aplicó a 15 estudiantes
When presiono el botón "Deshacer"
Then los estudiantes deben volver a sus estados anteriores
And debo ver el mensaje: "Acción deshecha exitosamente"
And el historial de cambios debe registrar la operación de deshacer
```

---

## HU-03: Cambiar Estado Individual de Asistencia

### Historia de Usuario
**Como** profesor,
**Quiero** cambiar el estado de asistencia de un estudiante específico con un clic,
**Para** corregir o actualizar su asistencia rápidamente.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Ciclar entre estados con un clic
```gherkin
Given que tengo una sesión de asistencia abierta
And el estudiante "Juan Pérez" (código: EST001) tiene estado "Presente"
When hago clic en la fila del estudiante "Juan Pérez"
Then su estado debe cambiar a "Ausente"
And el ícono debe cambiar a una X roja
When vuelvo a hacer clic en la fila
Then su estado debe cambiar a "Tardanza"
And el ícono debe cambiar a un reloj naranja
When hago clic nuevamente
Then su estado debe volver a "Presente"
And el ícono debe mostrar un check verde
```

#### Escenario 2: Actualización en tiempo real del contador
```gherkin
Given que tengo el contador mostrando: "10 Presentes, 3 Ausentes, 2 Tardanzas"
When cambio el estado de un estudiante de "Presente" a "Ausente"
Then el contador debe actualizarse inmediatamente a: "9 Presentes, 4 Ausentes, 2 Tardanzas"
And el cambio debe ser visible sin recargar la página
```

#### Escenario 3: Cambio de estado con selector desplegable
```gherkin
Given que tengo una sesión de asistencia abierta
When hago clic derecho en un estudiante
Then debo ver un menú contextual con opciones:
  - Marcar como Presente
  - Marcar como Ausente
  - Marcar como Tardanza
When selecciono "Marcar como Tardanza"
Then el estado del estudiante debe cambiar a "Tardanza"
And debo ver una animación de transición
```

---

## HU-04: Guardar Asistencia con Validación

### Historia de Usuario
**Como** profesor,
**Quiero** guardar la sesión de asistencia con validación de datos,
**Para** asegurar que la información quede registrada correctamente en el sistema.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Guardar sesión exitosamente
```gherkin
Given que he registrado la asistencia de todos los estudiantes
And el contador muestra: "12 Presentes, 2 Ausentes, 1 Tardanza"
When presiono el botón "Guardar Asistencia"
Then debo ver un mensaje de confirmación: "Asistencia guardada exitosamente"
And la sesión debe cambiar a estado "Cerrada"
And no debo poder modificar los estados
And debo ver la fecha y hora de guardado
```

#### Escenario 2: Validación de sesión incompleta
```gherkin
Given que tengo una sesión con 15 estudiantes
And solo he revisado 10 estudiantes
And 5 estudiantes no tienen registro de cambio
When intento guardar la asistencia
Then debo ver una advertencia: "Algunos estudiantes pueden no haber sido revisados"
And debo tener las opciones:
  - "Guardar De Todas Formas"
  - "Revisar Estudiantes"
```

#### Escenario 3: Autoguardado cada 30 segundos
```gherkin
Given que estoy registrando asistencia
And han pasado 30 segundos desde el último cambio
When realizo un cambio de estado
Then el sistema debe autoguardar automáticamente
And debo ver un indicador: "Autoguardado a las 14:35:22"
And el indicador debe desaparecer después de 3 segundos
```

#### Escenario 4: Error al guardar (sin conexión)
```gherkin
Given que estoy registrando asistencia
And se pierde la conexión a internet
When presiono "Guardar Asistencia"
Then debo ver un mensaje de error: "No se pudo guardar. Verifique su conexión"
And los datos deben mantenerse en localStorage
And debo ver un botón "Reintentar"
When restauro la conexión
And presiono "Reintentar"
Then la asistencia debe guardarse exitosamente
```

---

## HU-05: Ver Historial de Asistencia de un Estudiante

### Historia de Usuario
**Como** profesor,
**Quiero** ver el historial completo de asistencia de un estudiante,
**Para** identificar patrones de ausentismo y tomar decisiones informadas.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Ver historial completo
```gherkin
Given que estoy en una sesión de asistencia
When hago clic en el ícono de historial del estudiante "María García" (EST002)
Then debo ver un modal con:
  - Nombre completo y código institucional
  - Tabla con todas las sesiones de la materia actual
  - Columnas: Fecha, Estado, Hora Inicio, Hora Fin
And las filas deben estar ordenadas por fecha descendente
And debo ver estadísticas:
  | Métrica | Valor |
  | Total Sesiones | 20 |
  | Presentes | 16 |
  | Ausentes | 3 |
  | Tardanzas | 1 |
  | Porcentaje Asistencia | 80% |
```

#### Escenario 2: Filtrar historial por rango de fechas
```gherkin
Given que estoy viendo el historial de un estudiante
When selecciono el rango de fechas:
  | Fecha Inicio | 2026-01-01 |
  | Fecha Fin | 2026-01-15 |
And presiono "Filtrar"
Then debo ver solo las sesiones dentro de ese rango
And las estadísticas deben recalcularse para ese período
```

#### Escenario 3: Identificar estudiante con bajo porcentaje
```gherkin
Given que estoy viendo el historial de un estudiante
When el porcentaje de asistencia es menor al 70%
Then debo ver una alerta visual roja con el ícono ⚠️
And debo ver el mensaje: "Estudiante en riesgo por bajo porcentaje de asistencia"
```

---

## HU-06: Ver Dashboard de Alertas de Asistencia

### Historia de Usuario
**Como** profesor,
**Quiero** ver un dashboard con alertas de estudiantes en riesgo,
**Para** tomar acción temprana con estudiantes que tienen problemas de asistencia.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Ver dashboard con alertas activas
```gherkin
Given que soy profesor de 3 materias
And tengo 45 estudiantes en total
When accedo a "Dashboard de Asistencia"
Then debo ver un widget con:
  - "Alertas Activas: 5"
  - Lista de estudiantes con porcentaje < 70%
And cada alerta debe mostrar:
  | Campo | Descripción |
  | Nombre | Nombre completo del estudiante |
  | Materia | Nombre de la materia |
  | Porcentaje | Porcentaje actual de asistencia |
  | Última Ausencia | Fecha de la última sesión ausente |
  | Días Consecutivos | Número de ausencias consecutivas |
```

#### Escenario 2: Ordenar alertas por severidad
```gherkin
Given que tengo 5 alertas activas
When presiono "Ordenar por Severidad"
Then las alertas deben ordenarse por:
  - Prioridad 1 (Rojo): Porcentaje < 50%
  - Prioridad 2 (Naranja): Porcentaje < 60%
  - Prioridad 3 (Amarillo): Porcentaje < 70%
And las de mayor prioridad deben aparecer primero
```

#### Escenario 3: Filtrar alertas por materia
```gherkin
Given que tengo alertas en múltiples materias
When selecciono el filtro "Matemáticas Avanzadas"
Then debo ver solo las alertas de esa materia
And el contador debe actualizarse: "Alertas Activas: 2 (de 5 totales)"
```

#### Escenario 4: Exportar reporte de alertas
```gherkin
Given que tengo alertas activas
When presiono el botón "Exportar Reporte"
Then debo descargar un archivo PDF con:
  - Fecha de generación
  - Lista completa de estudiantes en alerta
  - Estadísticas por materia
  - Gráfico de tendencia de asistencia
And el archivo debe nombrarse: "alertas_asistencia_YYYYMMDD.pdf"
```

---

## HU-07: Generar Estadísticas de Asistencia por Materia

### Historia de Usuario
**Como** profesor,
**Quiero** ver estadísticas agregadas de asistencia de mi materia,
**Para** evaluar el nivel de compromiso general del grupo.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Ver estadísticas generales
```gherkin
Given que soy profesor de "Matemáticas Avanzadas"
And la materia tiene 20 sesiones registradas
When accedo a "Estadísticas de Asistencia"
Then debo ver un dashboard con:
  - Total de Sesiones: 20
  - Promedio de Asistencia: 85%
  - Gráfico de barras con distribución:
    | Estado | Cantidad | Porcentaje |
    | Presente | 255 | 85% |
    | Ausente | 30 | 10% |
    | Tardanza | 15 | 5% |
And debo ver un gráfico de línea mostrando la tendencia por semana
```

#### Escenario 2: Comparar entre períodos
```gherkin
Given que tengo estadísticas de asistencia
When selecciono "Comparar Períodos"
And elijo:
  | Período 1 | 2026-01-01 a 2026-01-15 |
  | Período 2 | 2025-12-01 a 2025-12-15 |
Then debo ver una comparación lado a lado con:
  - Promedio de asistencia de cada período
  - Diferencia porcentual
  - Indicador de mejora o deterioro
```

#### Escenario 3: Identificar día con mayor ausentismo
```gherkin
Given que tengo 20 sesiones registradas
When el sistema analiza los datos
Then debo ver una sección "Día con Mayor Ausentismo"
And debe mostrar:
  - Fecha: 2026-01-10
  - Ausentes: 8 estudiantes (40%)
  - Posible causa: Festivo o evento
```

---

## Resumen de Priorización (MoSCoW)

### Must Have (MVP)
- HU-01: Crear Sesión de Asistencia
- HU-02: Marcar Asistencia con Botones Masivos
- HU-03: Cambiar Estado Individual de Asistencia
- HU-04: Guardar Asistencia con Validación

### Should Have
- HU-05: Ver Historial de Asistencia de un Estudiante
- HU-06: Ver Dashboard de Alertas de Asistencia

### Could Have
- HU-07: Generar Estadísticas de Asistencia por Materia

---

## Métricas de Éxito

- **Tiempo promedio para registrar asistencia de 30 estudiantes:** < 2 minutos
- **Tasa de error en guardado de asistencia:** < 0.5%
- **Uso de botones masivos vs individual:** > 60% uso masivo
- **Tiempo de carga del historial:** < 1 segundo
- **Satisfacción del profesor:** > 4.5/5 estrellas

---

## Notas para Implementación TDD

1. **Orden de implementación:**
   - HU-04 (backend: modelos y validaciones)
   - HU-01 (endpoint de creación)
   - HU-03 (actualización individual)
   - HU-02 (actualización masiva)
   - HU-05, HU-06, HU-07 (reportes y estadísticas)

2. **Tests prioritarios:**
   - Unit: Validación de fechas y horas
   - Unit: Lógica de ciclo de estados (Presente → Ausente → Tardanza → Presente)
   - Integration: POST /api/v1/attendance/sessions
   - Integration: PATCH /api/v1/attendance/sessions/{id}/students/{student_id}
   - E2E: Flujo completo desde creación hasta guardado

3. **Edge cases críticos:**
   - Sesiones duplicadas en mismo día
   - Cambios concurrentes (dos profesores editando mismo estudiante)
   - Pérdida de conexión durante guardado
   - Más de 100 estudiantes en una clase
   - Sesiones con fecha/hora de fin antes que inicio
