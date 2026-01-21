---
title: Historias de Usuario - Importación y Exportación de Excel
version: 1.0
date_created: 2026-01-19
last_updated: 2026-01-19
---

# Historias de Usuario - Importación y Exportación de Excel

## Epic: Sistema de Gestión Masiva de Usuarios vía Excel

**Como** administrador del sistema académico,
**Quiero** importar y exportar datos de usuarios en formato Excel,
**Para** gestionar grandes cantidades de usuarios eficientemente y facilitar la integración con otros sistemas.

---

## HU-01: Descargar Plantilla de Excel

### Historia de Usuario
**Como** administrador,
**Quiero** descargar una plantilla de Excel con el formato correcto,
**Para** saber qué columnas debo completar al importar usuarios.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Descargar plantilla para importar usuarios
```gherkin
Given que estoy autenticado como administrador
When accedo a "Gestión de Usuarios"
And presiono el botón "Descargar Plantilla Excel"
Then debo descargar un archivo Excel con nombre: "plantilla_usuarios_YYYYMMDD.xlsx"
And el archivo debe contener una hoja llamada "Usuarios"
And la primera fila debe tener los encabezados:
  | Columna | Descripción | Obligatorio |
  | codigo_institucional | Código único | No (se genera automáticamente si vacío) |
  | nombre | Nombre completo | Sí |
  | email | Correo electrónico | Sí |
  | role | Admin/Profesor/Estudiante | Sí |
  | fecha_nacimiento | Formato: YYYY-MM-DD | Sí |
  | genero | M/F/Otro | No |
  | telefono | Número de teléfono | No |
And la segunda fila debe contener ejemplos de datos válidos
And el archivo debe incluir una hoja "Instrucciones" con:
  - Reglas de validación
  - Ejemplos de cada campo
  - Errores comunes a evitar
```

#### Escenario 2: Plantilla con datos de ejemplo
```gherkin
Given que descargo la plantilla
When abro el archivo Excel
Then debo ver 3 filas de ejemplo con datos realistas:
  | codigo_institucional | nombre | email | role | fecha_nacimiento |
  | EST001 | Juan Pérez | juan.perez@sofka.edu | Estudiante | 2000-05-15 |
  | PROF001 | María García | maria.garcia@sofka.edu | Profesor | 1985-08-22 |
  | | Pedro López | pedro.lopez@sofka.edu | Estudiante | 2001-03-10 |
And debo poder eliminar los ejemplos antes de llenar mis datos
```

---

## HU-02: Importar Usuarios desde Excel

### Historia de Usuario
**Como** administrador,
**Quiero** cargar un archivo Excel con usuarios,
**Para** crearlos o actualizarlos masivamente en el sistema.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Importación exitosa de nuevos usuarios
```gherkin
Given que tengo un archivo Excel con 10 usuarios nuevos
And todos los datos son válidos
When accedo a "Gestión de Usuarios"
And presiono "Importar desde Excel"
And selecciono mi archivo
And confirmo la importación
Then debo ver una pantalla de progreso mostrando: "Procesando 10 de 10 usuarios..."
And al finalizar debo ver el mensaje: "Importación completada: 10 usuarios creados, 0 actualizados, 0 errores"
And los 10 usuarios deben aparecer en la lista de usuarios
And cada usuario debe tener una contraseña temporal generada
And cada usuario debe recibir un email de bienvenida
```

#### Escenario 2: Actualización de usuarios existentes (Upsert)
```gherkin
Given que el sistema tiene un usuario con email "juan.perez@sofka.edu"
And cargo un Excel con una fila:
  | email | nombre | telefono |
  | juan.perez@sofka.edu | Juan Pérez Gómez | 3001234567 |
When importo el archivo
Then el sistema debe actualizar el usuario existente
And debo ver: "Importación completada: 0 usuarios creados, 1 actualizado, 0 errores"
And el nombre debe cambiar de "Juan Pérez" a "Juan Pérez Gómez"
And el teléfono debe actualizarse a "3001234567"
And NO debe cambiar el código institucional ni la contraseña
```

#### Escenario 3: Generación automática de códigos institucionales
```gherkin
Given que cargo un Excel con la columna codigo_institucional vacía:
  | codigo_institucional | nombre | email | role |
  | | María López | maria.lopez@sofka.edu | Estudiante |
  | | Pedro García | pedro.garcia@sofka.edu | Profesor |
When importo el archivo
Then el sistema debe generar códigos únicos:
  | Generado | Formato |
  | EST002 | EST + número secuencial |
  | PROF002 | PROF + número secuencial |
And debo ver en el reporte: "2 códigos institucionales generados automáticamente"
```

---

## HU-03: Validar Datos del Excel Antes de Importar

### Historia de Usuario
**Como** administrador,
**Quiero** que el sistema valide los datos del Excel antes de importarlos,
**Para** detectar errores sin afectar la base de datos.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Detectar emails inválidos
```gherkin
Given que cargo un Excel con emails inválidos:
  | nombre | email | role |
  | Juan Pérez | juan.perez | Estudiante |
  | María López | maria@invalido | Estudiante |
When inicio la importación
Then el sistema debe validar el archivo SIN guardar datos
And debo ver un reporte de errores:
  | Fila | Campo | Error | Valor |
  | 2 | email | Formato de email inválido | juan.perez |
  | 3 | email | Dominio no permitido | maria@invalido |
And debo ver el contador: "2 errores encontrados, 0 usuarios procesados"
And debo tener las opciones:
  - "Descargar Reporte de Errores"
  - "Corregir y Reintentar"
  - "Cancelar"
```

#### Escenario 2: Detectar roles inválidos
```gherkin
Given que cargo un Excel con rol inválido:
  | nombre | email | role |
  | Pedro Ruiz | pedro@sofka.edu | Director |
When valido el archivo
Then debo ver el error:
  | Fila | Campo | Error | Valor Permitidos |
  | 2 | role | Rol no válido | Admin, Profesor, Estudiante |
```

#### Escenario 3: Detectar fechas de nacimiento inválidas
```gherkin
Given que cargo un Excel con fechas inválidas:
  | nombre | fecha_nacimiento |
  | Ana Torres | 31/12/2010 |
  | Luis Mora | 2025-01-01 |
When valido el archivo
Then debo ver errores:
  | Fila | Error |
  | 2 | Formato de fecha incorrecto. Use: YYYY-MM-DD |
  | 3 | Fecha no puede ser futura |
And NO debe procesarse ningún usuario
```

#### Escenario 4: Detectar emails duplicados en el archivo
```gherkin
Given que cargo un Excel con emails repetidos:
  | nombre | email |
  | Juan Pérez | juan@sofka.edu |
  | Pedro López | juan@sofka.edu |
When valido el archivo
Then debo ver el error: "Email duplicado en filas 2 y 3: juan@sofka.edu"
And ambas filas deben marcarse como inválidas
```

---

## HU-04: Ver Reporte Detallado de Importación

### Historia de Usuario
**Como** administrador,
**Quiero** ver un reporte detallado después de cada importación,
**Para** saber exactamente qué usuarios se crearon, actualizaron o fallaron.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Reporte con importación mixta (éxitos y errores)
```gherkin
Given que importé un Excel con 15 usuarios
And 10 se crearon exitosamente
And 3 se actualizaron
And 2 tuvieron errores
When la importación finaliza
Then debo ver un modal con el resumen:
  | Métrica | Valor |
  | Total procesados | 15 |
  | Creados | 10 |
  | Actualizados | 3 |
  | Errores | 2 |
  | Tiempo de procesamiento | 3.2 segundos |
And debo ver tres pestañas:
  - "Creados" (10 registros)
  - "Actualizados" (3 registros)
  - "Errores" (2 registros)
```

#### Escenario 2: Ver detalle de usuarios creados
```gherkin
Given que estoy viendo el reporte de importación
When selecciono la pestaña "Creados"
Then debo ver una tabla con:
  | Código | Nombre | Email | Contraseña Temporal | Email Enviado |
  | EST003 | Juan López | juan.lopez@sofka.edu | TempPass123 | ✓ |
And debo poder copiar las contraseñas temporales
```

#### Escenario 3: Ver detalle de errores
```gherkin
Given que estoy viendo el reporte de importación
When selecciono la pestaña "Errores"
Then debo ver:
  | Fila | Nombre | Email | Error | Sugerencia |
  | 5 | María Torres | maria.torres@sofka.edu | Email ya existe | Actualice los datos del usuario existente |
  | 12 | Pedro Gómez | pedro | Email inválido | Use formato: usuario@dominio.com |
And debo poder exportar este reporte a Excel
```

#### Escenario 4: Descargar reporte completo en Excel
```gherkin
Given que he completado una importación
When presiono "Descargar Reporte Completo"
Then debo descargar un archivo: "reporte_importacion_YYYYMMDD_HHMMSS.xlsx"
And el archivo debe tener 3 hojas:
  - "Creados"
  - "Actualizados"
  - "Errores"
And cada hoja debe contener todos los detalles correspondientes
```

---

## HU-05: Exportar Usuarios a Excel

### Historia de Usuario
**Como** administrador,
**Quiero** exportar la lista completa de usuarios a Excel,
**Para** tener un respaldo, análisis o compartir con otras áreas.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Exportar todos los usuarios
```gherkin
Given que el sistema tiene 150 usuarios registrados
When accedo a "Gestión de Usuarios"
And presiono el botón "Exportar a Excel"
Then debo descargar un archivo: "usuarios_YYYYMMDD_HHMMSS.xlsx"
And el archivo debe contener 150 filas (más encabezados)
And las columnas deben ser:
  | Columna |
  | codigo_institucional |
  | nombre |
  | email |
  | role |
  | fecha_nacimiento |
  | genero |
  | telefono |
  | fecha_creacion |
  | ultimo_acceso |
  | estado |
And NO debe incluir contraseñas por seguridad
```

#### Escenario 2: Exportar usuarios filtrados
```gherkin
Given que he aplicado filtros:
  | Filtro | Valor |
  | Role | Estudiante |
  | Estado | Activo |
And hay 80 estudiantes activos
When presiono "Exportar a Excel"
Then el archivo debe contener solo los 80 estudiantes activos
And el nombre del archivo debe incluir el filtro: "usuarios_Estudiante_YYYYMMDD.xlsx"
```

#### Escenario 3: Exportar con límite de filas
```gherkin
Given que el sistema tiene 2000 usuarios
When intento exportar todos
Then debo ver un mensaje: "La exportación tiene un límite de 1000 registros"
And debo tener las opciones:
  - "Exportar primeros 1000"
  - "Aplicar filtros y exportar"
  - "Cancelar"
```

---

## HU-06: Validar Límite de Filas en Importación

### Historia de Usuario
**Como** administrador,
**Quiero** que el sistema limite la cantidad de usuarios a importar,
**Para** evitar sobrecargas en el servidor y errores de timeout.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Rechazo de archivo con más de 1000 filas
```gherkin
Given que cargo un archivo Excel con 1500 usuarios
When intento importar el archivo
Then debo ver el mensaje de error: "El archivo supera el límite de 1000 usuarios por importación"
And debo ver la sugerencia: "Divida el archivo en varios archivos más pequeños"
And la importación NO debe iniciarse
```

#### Escenario 2: Archivo dentro del límite
```gherkin
Given que cargo un archivo con 800 usuarios
When inicio la importación
Then el sistema debe procesar el archivo normalmente
And NO debe mostrar advertencias sobre límites
```

#### Escenario 3: Configuración del límite por administrador
```gherkin
Given que soy administrador con permisos avanzados
When accedo a "Configuración del Sistema"
And modifico el parámetro "max_import_rows" de 1000 a 2000
Then las futuras importaciones deben aceptar hasta 2000 filas
And debo ver un registro en el log de auditoría
```

---

## HU-07: Manejo de Contraseñas en Importación

### Historia de Usuario
**Como** administrador,
**Quiero** que el sistema genere contraseñas temporales seguras para usuarios nuevos,
**Para** garantizar la seguridad sin tener que crearlas manualmente.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Generación automática de contraseñas
```gherkin
Given que importo 20 usuarios nuevos
When la importación se completa
Then cada usuario debe tener una contraseña temporal con:
  - Longitud: 12 caracteres
  - Al menos 1 mayúscula
  - Al menos 1 minúscula
  - Al menos 1 número
  - Al menos 1 carácter especial
And las contraseñas deben ser únicas entre sí
And deben estar hasheadas con bcrypt en la base de datos
```

#### Escenario 2: Envío de credenciales por email
```gherkin
Given que importé 5 usuarios nuevos
When la importación finaliza
Then cada usuario debe recibir un email con:
  - Asunto: "Bienvenido a SIA SOFKA - Sus credenciales"
  - Código institucional
  - Contraseña temporal
  - Enlace para cambiar contraseña
  - Instrucciones de primer acceso
And debo ver en el reporte: "5 emails enviados exitosamente"
```

#### Escenario 3: Fallo en envío de emails
```gherkin
Given que el servidor de email no está disponible
When importo usuarios
Then los usuarios deben crearse de todas formas
And debo ver una advertencia: "3 usuarios creados, pero el envío de emails falló"
And debo tener la opción "Reenviar Emails"
And las contraseñas deben mostrarse en el reporte para entrega manual
```

#### Escenario 4: NO incluir contraseñas en exportaciones
```gherkin
Given que exporto usuarios a Excel
When abro el archivo exportado
Then NO debe existir una columna "contraseña" o "password"
And debe haber una nota en la hoja "Instrucciones": "Por seguridad, las contraseñas nunca se exportan"
```

---

## HU-08: Validar Formato de Archivo

### Historia de Usuario
**Como** administrador,
**Quiero** que el sistema valide el formato del archivo antes de procesarlo,
**Para** evitar errores por archivos corruptos o formatos incorrectos.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Rechazo de formatos no permitidos
```gherkin
Given que intento cargar un archivo CSV
When selecciono el archivo "usuarios.csv"
Then debo ver el error: "Formato no permitido. Solo se aceptan archivos .xlsx o .xls"
And el botón "Importar" debe estar deshabilitado
```

#### Escenario 2: Validación de columnas obligatorias
```gherkin
Given que cargo un Excel sin la columna "email"
When valido el archivo
Then debo ver el error: "Faltan columnas obligatorias: email, nombre, role"
And debo ver una lista de las columnas requeridas
```

#### Escenario 3: Validación de hoja del Excel
```gherkin
Given que cargo un Excel sin la hoja "Usuarios"
When intento importar
Then debo ver el error: "No se encontró la hoja 'Usuarios' en el archivo"
And debo ver las hojas disponibles: "Hoja1, Hoja2"
```

#### Escenario 4: Archivo vacío
```gherkin
Given que cargo un Excel con solo encabezados (sin datos)
When intento importar
Then debo ver el mensaje: "El archivo no contiene datos para importar"
And NO debe iniciarse el proceso de importación
```

---

## HU-09: Auditoría de Operaciones Masivas

### Historia de Usuario
**Como** administrador del sistema,
**Quiero** que queden registradas todas las operaciones de importación/exportación,
**Para** tener trazabilidad y cumplir con requisitos de auditoría.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Registro de importación en log de auditoría
```gherkin
Given que importo un archivo con 50 usuarios
When la importación finaliza
Then debe crearse un registro en el log de auditoría con:
  | Campo | Valor |
  | Acción | IMPORT_USERS |
  | Usuario | admin@sofka.edu |
  | Fecha y Hora | 2026-01-19 14:35:22 |
  | Archivo | usuarios_2026.xlsx |
  | Total Procesados | 50 |
  | Creados | 45 |
  | Actualizados | 5 |
  | Errores | 0 |
  | IP | 192.168.1.100 |
```

#### Escenario 2: Registro de exportación
```gherkin
Given que exporto 200 usuarios a Excel
When la descarga se completa
Then debe registrarse en auditoría:
  | Acción | EXPORT_USERS |
  | Filtros Aplicados | Role: Estudiante, Estado: Activo |
  | Cantidad Exportada | 200 |
```

#### Escenario 3: Consultar historial de operaciones masivas
```gherkin
Given que soy administrador
When accedo a "Auditoría > Operaciones Masivas"
Then debo ver una tabla con todas las importaciones/exportaciones
And debo poder filtrar por:
  - Fecha
  - Usuario que ejecutó
  - Tipo de operación (Importación/Exportación)
And debo poder descargar el historial en CSV
```

---

## HU-10: Actualización Parcial de Usuarios

### Historia de Usuario
**Como** administrador,
**Quiero** importar un Excel con solo algunos campos a actualizar,
**Para** modificar datos específicos sin tener que incluir toda la información.

### Criterios de Aceptación (Gherkin)

#### Escenario 1: Actualizar solo teléfonos
```gherkin
Given que el sistema tiene usuarios con emails:
  - juan@sofka.edu
  - maria@sofka.edu
And cargo un Excel con solo 2 columnas:
  | email | telefono |
  | juan@sofka.edu | 3001111111 |
  | maria@sofka.edu | 3002222222 |
When importo el archivo
Then deben actualizarse solo los teléfonos
And NO deben modificarse: nombre, fecha_nacimiento, role, etc.
And debo ver: "2 usuarios actualizados"
```

#### Escenario 2: Actualizar múltiples campos selectivamente
```gherkin
Given que cargo un Excel con:
  | email | telefono | genero |
  | pedro@sofka.edu | 3003333333 | M |
And el usuario pedro@sofka.edu existe
When importo
Then deben actualizarse telefono Y genero
And los demás campos deben permanecer intactos
```

#### Escenario 3: Validación de campos no actualizables
```gherkin
Given que cargo un Excel intentando actualizar el campo "codigo_institucional"
When valido el archivo
Then debo ver una advertencia: "El código institucional no puede modificarse una vez creado"
And debo poder continuar actualizando los demás campos
```

---

## Resumen de Priorización (MoSCoW)

### Must Have (MVP)
- HU-01: Descargar Plantilla de Excel
- HU-02: Importar Usuarios desde Excel
- HU-03: Validar Datos del Excel Antes de Importar
- HU-04: Ver Reporte Detallado de Importación
- HU-05: Exportar Usuarios a Excel
- HU-07: Manejo de Contraseñas en Importación

### Should Have
- HU-06: Validar Límite de Filas en Importación
- HU-08: Validar Formato de Archivo
- HU-09: Auditoría de Operaciones Masivas

### Could Have
- HU-10: Actualización Parcial de Usuarios

---

## Métricas de Éxito

- **Tiempo de importación de 100 usuarios:** < 10 segundos
- **Tasa de éxito en importaciones:** > 95%
- **Precisión en detección de errores:** 100%
- **Tiempo de exportación de 1000 usuarios:** < 5 segundos
- **Satisfacción del administrador:** > 4.5/5 estrellas

---

## Notas para Implementación TDD

1. **Orden de implementación:**
   - HU-01 (generación de plantilla con openpyxl)
   - HU-08 (validación de formato)
   - HU-03 (validación de datos con Pydantic)
   - HU-02 (lógica de upsert)
   - HU-07 (generación de contraseñas)
   - HU-05 (exportación con pandas)
   - HU-04, HU-06, HU-09, HU-10 (features avanzadas)

2. **Tests prioritarios:**
   - Unit: Validación de emails, fechas, roles
   - Unit: Generación de contraseñas seguras
   - Unit: Lógica de upsert (crear vs actualizar)
   - Integration: POST /api/v1/users/import
   - Integration: GET /api/v1/users/export
   - E2E: Flujo completo: descarga plantilla → llena datos → importa → valida

3. **Edge cases críticos:**
   - Archivo con 1001 filas (excede límite)
   - Emails duplicados entre archivo y BD
   - Caracteres especiales en nombres (ñ, tildes, diéresis)
   - Fechas en diferentes formatos (DD/MM/YYYY, MM-DD-YYYY)
   - Usuarios con rol inválido o campos vacíos
   - Código institucional duplicado
   - Actualización de campos protegidos (codigo_institucional, role)
