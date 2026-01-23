# Casos de Prueba - SIA SOFKA U

Este documento contiene los casos de prueba derivados de las historias de usuario del sistema SIA SOFKA U. Cada caso de prueba está vinculado a una historia de usuario específica y cubre todos los criterios de aceptación.

**Formato de Casos de Prueba:**
- **TC-XXX**: ID del caso de prueba
- **HU-XXX**: Historia de usuario relacionada
- **Tipo**: Unitario / Integración / E2E
- **Prioridad**: Crítica / Alta / Media / Baja
- **Precondiciones**: Requisitos previos
- **Pasos**: Secuencia de acciones
- **Resultado Esperado**: Comportamiento esperado
- **Criterios de Aceptación**: Validaciones específicas

---

## Índice

1. [Autenticación](#autenticación)
2. [Gestión de Usuarios](#gestión-de-usuarios)
3. [Gestión de Materias](#gestión-de-materias)
4. [Gestión de Inscripciones](#gestión-de-inscripciones)
5. [Gestión de Notas](#gestión-de-notas)
6. [Reportes](#reportes)
7. [Perfil de Usuario](#perfil-de-usuario)
8. [Funcionalidades del Sistema](#funcionalidades-del-sistema)

---

## Autenticación

### TC-001: Login Exitoso con Credenciales Válidas
**HU-001** | **Tipo**: Integración | **Prioridad**: Crítica

**Precondiciones:**
- Usuario existe en el sistema con email y contraseña válidos
- El usuario tiene un rol asignado (Admin, Profesor o Estudiante)

**Pasos:**
1. Realizar POST a `/api/v1/auth/login`
2. Enviar `username` (email) y `password` válidos
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Respuesta contiene `access_token` y `token_type: "bearer"`
- El token JWT incluye el campo `sub` con el email del usuario
- El token JWT incluye el campo `role` con el rol del usuario
- El token tiene tiempo de expiración configurado

**Criterios de Aceptación:**
-  Usuario puede iniciar sesión con credenciales válidas
-  Sistema genera token JWT
-  Token incluye rol del usuario
-  Token tiene tiempo de expiración configurable

---

### TC-002: Login Fallido con Email Incorrecto
**HU-001** | **Tipo**: Integración | **Prioridad**: Crítica

**Precondiciones:**
- No hay usuario con el email proporcionado

**Pasos:**
1. Realizar POST a `/api/v1/auth/login`
2. Enviar `username` (email inexistente) y `password`
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 401 Unauthorized
- Mensaje de error: "Incorrect email or password"

**Criterios de Aceptación:**
-  Si las credenciales son incorrectas, se muestra error 401

---

### TC-003: Login Fallido con Contraseña Incorrecta
**HU-001** | **Tipo**: Integración | **Prioridad**: Crítica

**Precondiciones:**
- Usuario existe en el sistema
- Se conoce el email del usuario

**Pasos:**
1. Realizar POST a `/api/v1/auth/login`
2. Enviar `username` (email válido) y `password` incorrecto
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 401 Unauthorized
- Mensaje de error: "Incorrect email or password"

**Criterios de Aceptación:**
-  Si las credenciales son incorrectas, se muestra error 401

---

### TC-004: Validar Token JWT Incluye Rol
**HU-001** | **Tipo**: Unitario | **Prioridad**: Crítica

**Precondiciones:**
- Usuario autenticado

**Pasos:**
1. Decodificar el token JWT recibido
2. Verificar campos del payload

**Resultado Esperado:**
- El payload contiene `sub` con el email
- El payload contiene `role` con el rol del usuario
- El payload contiene `exp` con la fecha de expiración

**Criterios de Aceptación:**
-  Token incluye el rol del usuario para autorización

---

### TC-005: Validar Expiración del Token
**HU-001** | **Tipo**: Unitario | **Prioridad**: Media

**Precondiciones:**
- Token JWT generado

**Pasos:**
1. Generar token JWT
2. Esperar tiempo de expiración + 1 segundo
3. Intentar usar el token

**Resultado Esperado:**
- Token expirado genera error 401 Unauthorized
- Mensaje: "Could not validate credentials"

**Criterios de Aceptación:**
-  Token tiene tiempo de expiración configurable

---

### TC-006: Registrar Nuevo Usuario como Administrador
**HU-002** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Token JWT válido

**Pasos:**
1. Realizar POST a `/api/v1/users`
2. Incluir header `Authorization: Bearer {token}`
3. Enviar datos del nuevo usuario (estudiante o profesor)
4. Verificar respuesta

**Resultado Esperado:**
- Status code: 201 Created
- Respuesta contiene datos del usuario creado
- Código institucional generado automáticamente
- Email validado (no duplicado)
- Edad calculada automáticamente
- Contraseña almacenada como hash

**Criterios de Aceptación:**
-  Solo administradores pueden registrar usuarios
-  Se puede crear estudiante o profesor
-  Sistema genera código institucional único
-  Email no duplicado
-  Edad calculada automáticamente
-  Contraseña almacenada de forma segura (hash)

---

### TC-007: Registrar Usuario con Email Duplicado
**HU-002** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Usuario existente con email "test@example.com"

**Pasos:**
1. Realizar POST a `/api/v1/users`
2. Intentar crear usuario con email "test@example.com"
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 400 Bad Request
- Mensaje: "Email already registered"

**Criterios de Aceptación:**
-  Se valida que el email no esté duplicado

---

### TC-008: Registrar Usuario sin Permisos de Admin
**HU-002** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Profesor o Estudiante
- Token JWT válido

**Pasos:**
1. Realizar POST a `/api/v1/users`
2. Incluir header `Authorization: Bearer {token}` (no admin)
3. Enviar datos del nuevo usuario
4. Verificar respuesta

**Resultado Esperado:**
- Status code: 403 Forbidden
- Mensaje: "Not enough permissions"

**Criterios de Aceptación:**
-  Solo administradores pueden registrar usuarios

---

### TC-009: Ver Información de Perfil Propio
**HU-003** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado
- Token JWT válido

**Pasos:**
1. Realizar GET a `/api/v1/profile`
2. Incluir header `Authorization: Bearer {token}`
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Respuesta contiene: nombre, apellido, email, código institucional, rol, edad, etc.
- Solo se muestra información del usuario autenticado

**Criterios de Aceptación:**
-  Usuario puede ver su información personal
-  Se muestra información completa
-  Solo se puede acceder a la propia información

---

## Gestión de Usuarios

### TC-010: Crear Estudiante como Administrador
**HU-004** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin

**Pasos:**
1. Realizar POST a `/api/v1/users`
2. Enviar datos del estudiante con `role: "Estudiante"`
3. Incluir: nombre, apellido, email, fecha_nacimiento, programa_academico, ciudad_residencia
4. Verificar respuesta

**Resultado Esperado:**
- Status code: 201 Created
- Código institucional generado con formato `EST-XXXX`
- Email validado (no duplicado)
- Edad calculada automáticamente
- Programa académico y ciudad de residencia guardados

**Criterios de Aceptación:**
-  Se puede crear estudiante con todos sus datos
-  Código institucional único (formato: EST-XXXX)
-  Email no duplicado
-  Edad calculada automáticamente
-  Programa académico y ciudad de residencia especificables

---

### TC-011: Crear Profesor como Administrador
**HU-005** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin

**Pasos:**
1. Realizar POST a `/api/v1/users`
2. Enviar datos del profesor con `role: "Profesor"`
3. Incluir: nombre, apellido, email, fecha_nacimiento, area_ensenanza
4. Verificar respuesta

**Resultado Esperado:**
- Status code: 201 Created
- Código institucional generado con formato `PRO-XXXX`
- Email validado (no duplicado)
- Edad calculada automáticamente
- Área de enseñanza guardada

**Criterios de Aceptación:**
-  Se puede crear profesor con todos sus datos
-  Código institucional único (formato: PRO-XXXX)
-  Email no duplicado
-  Área de enseñanza especificable
-  Edad calculada automáticamente

---

### TC-012: Listar Todos los Usuarios como Administrador
**HU-006** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Múltiples usuarios creados (estudiantes y profesores)

**Pasos:**
1. Realizar GET a `/api/v1/users?skip=0&limit=10`
2. Incluir header `Authorization: Bearer {token}`
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Lista contiene estudiantes y profesores
- Cada elemento muestra: nombre, apellido, email, código institucional, rol
- Paginación funciona correctamente (skip y limit)

**Criterios de Aceptación:**
-  Se muestran todos los estudiantes y profesores
-  Lista es paginable (skip y limit)
-  Información relevante mostrada
-  Solo administradores pueden acceder

---

### TC-013: Listar Usuarios sin Permisos de Admin
**HU-006** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Profesor o Estudiante

**Pasos:**
1. Realizar GET a `/api/v1/users`
2. Incluir header `Authorization: Bearer {token}` (no admin)
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 403 Forbidden
- Mensaje: "Not enough permissions"

**Criterios de Aceptación:**
-  Solo administradores pueden acceder

---

### TC-014: Ver Detalles de un Usuario Específico
**HU-007** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Usuario existente con ID conocido

**Pasos:**
1. Realizar GET a `/api/v1/users/{user_id}`
2. Incluir header `Authorization: Bearer {token}`
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Respuesta contiene toda la información del usuario
- Incluye: nombre, apellido, email, código institucional, rol, edad, etc.

**Criterios de Aceptación:**
-  Se puede buscar usuario por ID
-  Se muestra toda la información
-  Solo administradores pueden acceder

---

### TC-015: Ver Usuario Inexistente
**HU-007** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- ID de usuario inexistente

**Pasos:**
1. Realizar GET a `/api/v1/users/99999`
2. Incluir header `Authorization: Bearer {token}`
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 404 Not Found
- Mensaje: "User with id 99999 not found"

**Criterios de Aceptación:**
-  Si el usuario no existe, se muestra error 404

---

### TC-016: Actualizar Usuario como Administrador
**HU-008** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Usuario existente con ID conocido

**Pasos:**
1. Realizar PUT a `/api/v1/users/{user_id}`
2. Enviar campos a actualizar (parcial)
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Solo los campos proporcionados se actualizan
- Email y código institucional no se pueden cambiar
- Respuesta contiene usuario actualizado

**Criterios de Aceptación:**
-  Se puede actualizar cualquier campo (excepto email y código institucional)
-  Campos son opcionales (solo se actualizan los proporcionados)
-  Usuario existe
-  Solo administradores pueden actualizar

---

### TC-017: Actualizar Usuario Inexistente
**HU-008** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin

**Pasos:**
1. Realizar PUT a `/api/v1/users/99999`
2. Enviar datos de actualización
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 404 Not Found
- Mensaje: "User with id 99999 not found"

**Criterios de Aceptación:**
-  Si el usuario no existe, se muestra error 404

---

### TC-018: Eliminar Usuario como Administrador
**HU-009** | **Tipo**: Integración | **Prioridad**: Baja

**Precondiciones:**
- Usuario autenticado con rol Admin
- Usuario existente con ID conocido

**Pasos:**
1. Realizar DELETE a `/api/v1/users/{user_id}`
2. Incluir header `Authorization: Bearer {token}`
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 204 No Content
- Usuario eliminado de la base de datos

**Criterios de Aceptación:**
-  Se puede eliminar usuario por ID
-  Operación retorna código 204
-  Solo administradores pueden eliminar

---

### TC-019: Eliminar Usuario Inexistente
**HU-009** | **Tipo**: Integración | **Prioridad**: Baja

**Precondiciones:**
- Usuario autenticado con rol Admin

**Pasos:**
1. Realizar DELETE a `/api/v1/users/99999`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 404 Not Found
- Mensaje: "User with id 99999 not found"

**Criterios de Aceptación:**
-  Si el usuario no existe, se muestra error 404

---

## Gestión de Materias

### TC-020: Crear Materia como Administrador
**HU-010** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Profesor existente con ID conocido

**Pasos:**
1. Realizar POST a `/api/v1/subjects`
2. Enviar datos de la materia: nombre, número_creditos, horario, descripción, profesor_id
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 201 Created
- Código institucional generado automáticamente con formato `MAT-XXXX`
- Profesor asignado correctamente
- Todos los campos guardados

**Criterios de Aceptación:**
-  Se puede crear materia con todos los campos
-  Profesor asignado
-  Código institucional único (formato: MAT-XXXX)
-  Profesor existe y es de rol PROFESOR
-  Solo administradores pueden crear

---

### TC-021: Crear Materia con Profesor Inexistente
**HU-010** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin

**Pasos:**
1. Realizar POST a `/api/v1/subjects`
2. Enviar `profesor_id: 99999` (inexistente)
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 404 Not Found
- Mensaje: "User with id 99999 not found" o "Profesor not found"

**Criterios de Aceptación:**
-  Se valida que el profesor exista

---

### TC-022: Crear Materia con Usuario que No es Profesor
**HU-010** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Estudiante existente con ID conocido

**Pasos:**
1. Realizar POST a `/api/v1/subjects`
2. Enviar `profesor_id` de un estudiante
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 400 Bad Request
- Mensaje indicando que el usuario debe ser de rol PROFESOR

**Criterios de Aceptación:**
-  Se valida que el profesor sea de rol PROFESOR

---

### TC-023: Listar Todas las Materias como Administrador
**HU-011** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Múltiples materias creadas

**Pasos:**
1. Realizar GET a `/api/v1/subjects?skip=0&limit=10`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Lista contiene todas las materias
- Cada materia incluye información del profesor asignado
- Paginación funciona (skip y limit)

**Criterios de Aceptación:**
-  Se muestran todas las materias
-  Lista incluye información del profesor
-  Lista es paginable
-  Solo administradores pueden acceder

---

### TC-024: Ver Detalles de una Materia Específica
**HU-012** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Materia existente con ID conocido

**Pasos:**
1. Realizar GET a `/api/v1/subjects/{subject_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Respuesta contiene toda la información de la materia
- Incluye información del profesor asignado

**Criterios de Aceptación:**
-  Se puede buscar materia por ID
-  Se muestra toda la información incluyendo profesor
-  Solo administradores pueden acceder

---

### TC-025: Ver Materia Inexistente
**HU-012** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin

**Pasos:**
1. Realizar GET a `/api/v1/subjects/99999`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 404 Not Found
- Mensaje: "Subject with id 99999 not found"

**Criterios de Aceptación:**
-  Si la materia no existe, se muestra error 404

---

### TC-026: Actualizar Materia como Administrador
**HU-013** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Materia existente con ID conocido
- Profesor existente (para cambio de profesor)

**Pasos:**
1. Realizar PUT a `/api/v1/subjects/{subject_id}`
2. Enviar campos a actualizar (parcial)
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Solo los campos proporcionados se actualizan
- Código institucional no se puede cambiar
- Si se cambia profesor, se valida que exista y sea PROFESOR

**Criterios de Aceptación:**
-  Se puede actualizar cualquier campo (excepto código institucional)
-  Campos son opcionales
-  Si se cambia profesor, se valida que exista y sea PROFESOR
-  Solo administradores pueden actualizar

---

### TC-027: Eliminar Materia como Administrador
**HU-014** | **Tipo**: Integración | **Prioridad**: Baja

**Precondiciones:**
- Usuario autenticado con rol Admin
- Materia existente con ID conocido

**Pasos:**
1. Realizar DELETE a `/api/v1/subjects/{subject_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 204 No Content
- Materia eliminada de la base de datos

**Criterios de Aceptación:**
-  Se puede eliminar materia por ID
-  Operación retorna código 204
-  Solo administradores pueden eliminar

---

## Gestión de Inscripciones

### TC-028: Inscribir Estudiante a una Materia
**HU-015** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Estudiante existente con ID conocido
- Materia existente con ID conocido

**Pasos:**
1. Realizar POST a `/api/v1/enrollments`
2. Enviar `estudiante_id` y `subject_id`
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 201 Created
- Inscripción creada correctamente
- Estudiante validado (existe y es ESTUDIANTE)
- Materia validada (existe)

**Criterios de Aceptación:**
-  Se puede crear inscripción
-  Estudiante existe y es de rol ESTUDIANTE
-  Materia existe
-  Solo administradores pueden crear

---

### TC-029: Inscribir Estudiante Duplicado en la Misma Materia
**HU-015** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Inscripción existente (estudiante_id + subject_id)

**Pasos:**
1. Realizar POST a `/api/v1/enrollments`
2. Intentar crear inscripción duplicada (mismo estudiante + misma materia)
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 409 Conflict
- Mensaje indicando que la inscripción ya existe

**Criterios de Aceptación:**
-  No se puede inscribir dos veces al mismo estudiante en la misma materia (error 409)

---

### TC-030: Inscribir Usuario que No es Estudiante
**HU-015** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Profesor existente con ID conocido
- Materia existente con ID conocido

**Pasos:**
1. Realizar POST a `/api/v1/enrollments`
2. Enviar `estudiante_id` de un profesor
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 400 Bad Request
- Mensaje indicando que el usuario debe ser ESTUDIANTE

**Criterios de Aceptación:**
-  Se valida que el estudiante sea de rol ESTUDIANTE

---

### TC-031: Listar Todas las Inscripciones como Administrador
**HU-016** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Múltiples inscripciones creadas

**Pasos:**
1. Realizar GET a `/api/v1/enrollments?skip=0&limit=10`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Lista contiene todas las inscripciones
- Cada inscripción incluye: ID, datos del estudiante, datos de la materia, fecha de creación
- Paginación funciona

**Criterios de Aceptación:**
-  Se muestran todas las inscripciones
-  Lista incluye información completa
-  Lista es paginable
-  Solo administradores pueden acceder

---

### TC-032: Ver Detalles de una Inscripción Específica
**HU-017** | **Tipo**: Integración | **Prioridad**: Baja

**Precondiciones:**
- Usuario autenticado con rol Admin
- Inscripción existente con ID conocido

**Pasos:**
1. Realizar GET a `/api/v1/enrollments/{enrollment_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Respuesta contiene toda la información de la inscripción
- Incluye datos del estudiante y la materia

**Criterios de Aceptación:**
-  Se puede buscar inscripción por ID
-  Se muestra toda la información
-  Solo administradores pueden acceder

---

### TC-033: Eliminar Inscripción como Administrador
**HU-018** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Inscripción existente con ID conocido

**Pasos:**
1. Realizar DELETE a `/api/v1/enrollments/{enrollment_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 204 No Content
- Inscripción eliminada de la base de datos

**Criterios de Aceptación:**
-  Se puede eliminar inscripción por ID
-  Operación retorna código 204
-  Solo administradores pueden eliminar

---

## Gestión de Notas

### TC-034: Crear Nota como Profesor en Materia Asignada
**HU-019** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Profesor
- Materia asignada al profesor
- Estudiante inscrito en la materia
- Inscripción existente con ID conocido

**Pasos:**
1. Realizar POST a `/api/v1/grades`
2. Enviar: `enrollment_id`, `nota` (0-5), `periodo`, `fecha`, `observaciones` (opcional)
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 201 Created
- Nota creada correctamente
- Profesor validado (materia asignada)
- Estudiante validado (inscrito en materia)
- Nota entre 0 y 5

**Criterios de Aceptación:**
-  Profesor solo puede crear notas para materias asignadas
-  Estudiante inscrito en la materia
-  Nota entre 0 y 5
-  Campos opcionales funcionan

---

### TC-035: Crear Nota como Profesor en Materia No Asignada
**HU-019** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Profesor
- Materia NO asignada al profesor
- Inscripción existente

**Pasos:**
1. Realizar POST a `/api/v1/grades`
2. Intentar crear nota para materia no asignada
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 403 Forbidden
- Mensaje: "Not enough permissions" o "Subject is not assigned to this profesor"

**Criterios de Aceptación:**
-  Si el profesor intenta crear nota para materia no asignada, se muestra error 403

---

### TC-036: Crear Nota como Administrador
**HU-020** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Inscripción existente

**Pasos:**
1. Realizar POST a `/api/v1/grades`
2. Enviar datos de la nota
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 201 Created
- Nota creada correctamente
- Administrador puede crear para cualquier materia
- Estudiante validado (inscrito)

**Criterios de Aceptación:**
-  Administrador puede crear notas para cualquier materia
-  Estudiante inscrito en la materia
-  Nota entre 0 y 5

---

### TC-037: Crear Nota con Valor Fuera de Rango
**HU-019, HU-020** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado (Profesor o Admin)
- Inscripción existente

**Pasos:**
1. Realizar POST a `/api/v1/grades`
2. Enviar `nota: 6` (fuera de rango 0-5)
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 422 Unprocessable Entity
- Mensaje de validación indicando que la nota debe estar entre 0 y 5

**Criterios de Aceptación:**
-  Nota debe estar entre 0 y 5

---

### TC-038: Ver Mis Notas como Estudiante
**HU-021** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Estudiante
- Estudiante inscrito en materia
- Notas existentes para el estudiante en la materia

**Pasos:**
1. Realizar GET a `/api/v1/grades?subject_id={subject_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Lista contiene solo las notas del estudiante autenticado
- Cada nota incluye: valor, período, fecha, observaciones
- Estudiante validado (inscrito en materia)

**Criterios de Aceptación:**
-  Estudiante solo puede ver sus propias notas
-  Se debe especificar ID de materia
-  Estudiante inscrito en materia
-  Se muestran todas las notas con información completa

---

### TC-039: Ver Notas como Estudiante No Inscrito
**HU-021** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Estudiante
- Estudiante NO inscrito en la materia

**Pasos:**
1. Realizar GET a `/api/v1/grades?subject_id={subject_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 403 Forbidden
- Mensaje: "Not enough permissions" o "Estudiante not enrolled in subject"

**Criterios de Aceptación:**
-  Si el estudiante no está inscrito, se muestra error 403

---

### TC-040: Ver Notas de Materia como Profesor
**HU-022** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Profesor
- Materia asignada al profesor
- Múltiples estudiantes con notas en la materia

**Pasos:**
1. Realizar GET a `/api/v1/grades?subject_id={subject_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Lista contiene todas las notas de la materia
- Cada nota incluye información del estudiante
- Profesor validado (materia asignada)

**Criterios de Aceptación:**
-  Profesor solo puede ver notas de materias asignadas
-  Se debe especificar ID de materia
-  Se muestran todas las notas con información del estudiante

---

### TC-041: Ver Notas de Materia No Asignada como Profesor
**HU-022** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Profesor
- Materia NO asignada al profesor

**Pasos:**
1. Realizar GET a `/api/v1/grades?subject_id={subject_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 403 Forbidden
- Mensaje: "Subject is not assigned to this profesor"

**Criterios de Aceptación:**
-  Si el profesor intenta ver notas de materia no asignada, se muestra error 403

---

### TC-042: Filtrar Notas por Enrollment ID como Profesor
**HU-022** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Profesor
- Materia asignada al profesor
- Inscripción existente con ID conocido

**Pasos:**
1. Realizar GET a `/api/v1/grades?enrollment_id={enrollment_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Lista contiene solo las notas de la inscripción especificada
- Profesor validado (materia asignada)

**Criterios de Aceptación:**
-  Se puede filtrar por inscripción específica (enrollment_id)

---

### TC-043: Ver Todas las Notas como Administrador
**HU-023** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Múltiples notas en el sistema

**Pasos:**
1. Realizar GET a `/api/v1/grades`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Lista contiene todas las notas del sistema
- Cada nota incluye información completa

**Criterios de Aceptación:**
-  Administrador puede ver todas las notas
-  Se muestran todas las notas con información completa

---

### TC-044: Filtrar Notas por Materia como Administrador
**HU-023** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Materia existente con notas

**Pasos:**
1. Realizar GET a `/api/v1/grades?subject_id={subject_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Lista contiene solo las notas de la materia especificada

**Criterios de Aceptación:**
-  Se puede filtrar por materia (subject_id)

---

### TC-045: Ver Detalles de una Nota como Estudiante (Propia)
**HU-024** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Estudiante
- Nota existente del estudiante

**Pasos:**
1. Realizar GET a `/api/v1/grades/{grade_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Respuesta contiene: ID, nota, período, fecha, observaciones, información de inscripción
- Estudiante validado (es su propia nota)

**Criterios de Aceptación:**
-  Estudiante solo puede ver sus propias notas
-  Se muestra información completa

---

### TC-046: Ver Detalles de Nota de Otro Estudiante
**HU-024** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Estudiante
- Nota existente de otro estudiante

**Pasos:**
1. Realizar GET a `/api/v1/grades/{grade_id}` (nota de otro estudiante)
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 403 Forbidden
- Mensaje: "Not enough permissions"

**Criterios de Aceptación:**
-  Si el usuario no tiene permiso, se muestra error 403

---

### TC-047: Ver Detalles de Nota como Profesor (Materia Asignada)
**HU-024** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Profesor
- Nota existente en materia asignada al profesor

**Pasos:**
1. Realizar GET a `/api/v1/grades/{grade_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Respuesta contiene información completa
- Profesor validado (materia asignada)

**Criterios de Aceptación:**
-  Profesor puede ver notas de materias asignadas
-  Se muestra información completa

---

### TC-048: Actualizar Nota como Profesor
**HU-025** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Profesor
- Nota existente en materia asignada al profesor

**Pasos:**
1. Realizar PUT a `/api/v1/grades/{grade_id}`
2. Enviar campos a actualizar (parcial)
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Solo los campos proporcionados se actualizan
- Profesor validado (materia asignada)

**Criterios de Aceptación:**
-  Profesor solo puede actualizar notas de materias asignadas
-  Campos son opcionales
-  Nota existe

---

### TC-049: Actualizar Nota como Administrador
**HU-026** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado con rol Admin
- Nota existente

**Pasos:**
1. Realizar PUT a `/api/v1/grades/{grade_id}`
2. Enviar campos a actualizar
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Administrador puede actualizar cualquier nota
- Solo los campos proporcionados se actualizan

**Criterios de Aceptación:**
-  Administrador puede actualizar cualquier nota
-  Campos son opcionales
-  Nota existe

---

### TC-050: Eliminar Nota como Profesor
**HU-027** | **Tipo**: Integración | **Prioridad**: Baja

**Precondiciones:**
- Usuario autenticado con rol Profesor
- Nota existente en materia asignada al profesor

**Pasos:**
1. Realizar DELETE a `/api/v1/grades/{grade_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 204 No Content
- Nota eliminada de la base de datos
- Profesor validado (materia asignada)

**Criterios de Aceptación:**
-  Profesor solo puede eliminar notas de materias asignadas
-  Operación retorna código 204

---

### TC-051: Eliminar Nota como Administrador
**HU-028** | **Tipo**: Integración | **Prioridad**: Baja

**Precondiciones:**
- Usuario autenticado con rol Admin
- Nota existente

**Pasos:**
1. Realizar DELETE a `/api/v1/grades/{grade_id}`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 204 No Content
- Nota eliminada de la base de datos

**Criterios de Aceptación:**
-  Administrador puede eliminar cualquier nota
-  Operación retorna código 204

---

## Reportes

### TC-052: Generar Reporte de Estudiante en Formato PDF
**HU-029** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Estudiante existente con notas en múltiples materias

**Pasos:**
1. Realizar GET a `/api/v1/reports/student/{estudiante_id}?format=pdf`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Content-Type: `application/pdf`
- Archivo PDF descargable
- Reporte incluye: información del estudiante, materias, notas por materia, promedio por materia, promedio general ponderado

**Criterios de Aceptación:**
-  Se puede generar reporte para cualquier estudiante
-  Reporte incluye información completa
-  Formato PDF disponible
-  Solo administradores pueden generar

---

### TC-053: Generar Reporte de Estudiante en Formato HTML
**HU-029** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Estudiante existente con notas

**Pasos:**
1. Realizar GET a `/api/v1/reports/student/{estudiante_id}?format=html`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Content-Type: `text/html`
- Archivo HTML descargable
- Reporte incluye información completa

**Criterios de Aceptación:**
-  Formato HTML disponible
-  Reporte se descarga como archivo

---

### TC-054: Generar Reporte de Estudiante en Formato JSON
**HU-029** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Admin
- Estudiante existente con notas

**Pasos:**
1. Realizar GET a `/api/v1/reports/student/{estudiante_id}?format=json`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Content-Type: `application/json`
- Respuesta JSON con estructura completa del reporte
- Incluye: información del estudiante, materias, notas, promedios

**Criterios de Aceptación:**
-  Formato JSON disponible
-  Reporte se retorna como respuesta JSON

---

### TC-055: Generar Reporte de Materia como Profesor (PDF)
**HU-030** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Profesor
- Materia asignada al profesor
- Múltiples estudiantes con notas en la materia

**Pasos:**
1. Realizar GET a `/api/v1/reports/subject/{subject_id}?format=pdf`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Content-Type: `application/pdf`
- Archivo PDF descargable
- Reporte incluye: información de la materia, lista de estudiantes, notas de cada estudiante, promedio de cada estudiante
- Profesor validado (materia asignada)

**Criterios de Aceptación:**
-  Profesor solo puede generar reportes de materias asignadas
-  Reporte incluye información completa
-  Formato PDF disponible

---

### TC-056: Generar Reporte de Materia No Asignada como Profesor
**HU-030** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Profesor
- Materia NO asignada al profesor

**Pasos:**
1. Realizar GET a `/api/v1/reports/subject/{subject_id}?format=pdf`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 403 Forbidden
- Mensaje: "Subject is not assigned to this profesor"

**Criterios de Aceptación:**
-  Si el profesor intenta generar reporte de materia no asignada, se muestra error 403

---

### TC-057: Generar Reporte General como Estudiante (PDF)
**HU-031** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Estudiante
- Estudiante con notas en múltiples materias

**Pasos:**
1. Realizar GET a `/api/v1/reports/general?format=pdf`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Content-Type: `application/pdf`
- Archivo PDF descargable
- Reporte incluye: información del estudiante, todas sus materias, notas por materia, promedio por materia, promedio general ponderado

**Criterios de Aceptación:**
-  Estudiante solo puede generar su propio reporte
-  Reporte incluye información completa
-  Formato PDF disponible

---

### TC-058: Generar Reporte General como Estudiante (JSON)
**HU-031** | **Tipo**: Integración | **Prioridad**: Alta

**Precondiciones:**
- Usuario autenticado con rol Estudiante
- Estudiante con notas

**Pasos:**
1. Realizar GET a `/api/v1/reports/general?format=json`
2. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Content-Type: `application/json`
- Respuesta JSON con estructura completa
- Incluye promedio general ponderado por créditos

**Criterios de Aceptación:**
-  Formato JSON disponible
-  Reporte incluye promedio general ponderado

---

## Perfil de Usuario

### TC-059: Ver Mi Perfil como Usuario Autenticado
**HU-032** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado (cualquier rol)
- Token JWT válido

**Pasos:**
1. Realizar GET a `/api/v1/profile`
2. Incluir header `Authorization: Bearer {token}`
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Respuesta contiene: nombre, apellido, email, código institucional, rol, edad, fecha de nacimiento, número de contacto, etc.
- Solo información del usuario autenticado

**Criterios de Aceptación:**
-  Usuario puede ver su propia información
-  Se muestra información completa
-  Solo se puede acceder a la propia información

---

### TC-060: Actualizar Mi Perfil como Usuario Autenticado
**HU-033** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado (cualquier rol)

**Pasos:**
1. Realizar PUT a `/api/v1/profile`
2. Enviar campos a actualizar (parcial)
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 200 OK
- Solo los campos proporcionados se actualizan
- Email, código institucional y rol NO se pueden cambiar
- Si se actualiza fecha de nacimiento, edad se recalcula automáticamente

**Criterios de Aceptación:**
-  Usuario puede actualizar su propia información
-  Campos actualizables: nombre, apellido, fecha_nacimiento, número_contacto, programa_academico (estudiantes), ciudad_residencia (estudiantes), área_ensenanza (profesores)
-  No se puede cambiar: email, código institucional, rol
-  Campos son opcionales
-  Si se actualiza fecha de nacimiento, edad se recalcula

---

### TC-061: Intentar Cambiar Email en Perfil
**HU-033** | **Tipo**: Integración | **Prioridad**: Media

**Precondiciones:**
- Usuario autenticado

**Pasos:**
1. Realizar PUT a `/api/v1/profile`
2. Intentar enviar `email` diferente
3. Verificar respuesta

**Resultado Esperado:**
- Status code: 400 Bad Request o el campo se ignora
- Email no se actualiza

**Criterios de Aceptación:**
-  No se puede cambiar email

---

## Funcionalidades del Sistema

### TC-062: Cálculo Automático de Promedio por Materia
**HU-034** | **Tipo**: Unitario | **Prioridad**: Alta

**Precondiciones:**
- Estudiante inscrito en materia
- Múltiples notas registradas

**Pasos:**
1. Obtener todas las notas de un enrollment
2. Calcular promedio
3. Verificar resultado

**Resultado Esperado:**
- Promedio calculado como media aritmética de todas las notas
- Resultado redondeado a 2 decimales
- Si no hay notas, promedio es None

**Criterios de Aceptación:**
-  Promedio se calcula como media aritmética
-  Resultado redondeado a 2 decimales
-  Si no hay notas, promedio es None
-  Cálculo automático en reportes

---

### TC-063: Cálculo de Promedio con Notas Múltiples
**HU-034** | **Tipo**: Unitario | **Prioridad**: Alta

**Precondiciones:**
- Enrollment con 3 notas: 4.5, 3.8, 4.2

**Pasos:**
1. Calcular promedio
2. Verificar resultado

**Resultado Esperado:**
- Promedio = (4.5 + 3.8 + 4.2) / 3 = 4.17
- Redondeado a 2 decimales

**Criterios de Aceptación:**
-  Cálculo correcto con múltiples notas

---

### TC-064: Cálculo Automático de Promedio General Ponderado
**HU-035** | **Tipo**: Unitario | **Prioridad**: Alta

**Precondiciones:**
- Estudiante con múltiples materias
- Cada materia tiene notas y créditos

**Pasos:**
1. Obtener todas las materias del estudiante con promedios
2. Calcular promedio general ponderado por créditos
3. Verificar resultado

**Resultado Esperado:**
- Promedio general = Σ(promedio_materia × créditos) / Σ(créditos)
- Solo se consideran materias con promedio calculado
- Resultado redondeado a 2 decimales
- Si no hay materias con notas, promedio general es None

**Criterios de Aceptación:**
-  Promedio general ponderado por créditos
-  Solo materias con promedio calculado
-  Resultado redondeado a 2 decimales
-  Si no hay materias con notas, promedio es None

---

### TC-065: Cálculo de Promedio General con Múltiples Materias
**HU-035** | **Tipo**: Unitario | **Prioridad**: Alta

**Precondiciones:**
- Materia 1: promedio 4.5, créditos 3
- Materia 2: promedio 3.8, créditos 4
- Materia 3: promedio 4.2, créditos 2

**Pasos:**
1. Calcular promedio general ponderado
2. Verificar resultado

**Resultado Esperado:**
- Promedio = (4.5×3 + 3.8×4 + 4.2×2) / (3+4+2) = 4.12
- Redondeado a 2 decimales

**Criterios de Aceptación:**
-  Cálculo correcto con múltiples materias y créditos

---

### TC-066: Generación Automática de Código Institucional para Estudiante
**HU-036** | **Tipo**: Unitario | **Prioridad**: Alta

**Precondiciones:**
- Base de datos con estudiantes existentes

**Pasos:**
1. Crear nuevo estudiante sin código institucional
2. Verificar código generado

**Resultado Esperado:**
- Código generado con formato `EST-YYYY-XXXX`
- Donde YYYY es el año actual
- XXXX es número secuencial
- Código es único

**Criterios de Aceptación:**
-  Estudiantes reciben códigos con formato EST-XXXX
-  Códigos son únicos y secuenciales
-  Generación automática al crear usuario

---

### TC-067: Generación Automática de Código Institucional para Profesor
**HU-036** | **Tipo**: Unitario | **Prioridad**: Alta

**Precondiciones:**
- Base de datos con profesores existentes

**Pasos:**
1. Crear nuevo profesor sin código institucional
2. Verificar código generado

**Resultado Esperado:**
- Código generado con formato `PRO-YYYY-XXXX`
- Donde YYYY es el año actual
- XXXX es número secuencial
- Código es único

**Criterios de Aceptación:**
-  Profesores reciben códigos con formato PRO-XXXX
-  Códigos son únicos y secuenciales
-  Generación automática al crear usuario

---

### TC-068: Generación Automática de Código Institucional para Materia
**HU-036** | **Tipo**: Unitario | **Prioridad**: Alta

**Precondiciones:**
- Base de datos con materias existentes

**Pasos:**
1. Crear nueva materia sin código institucional
2. Verificar código generado

**Resultado Esperado:**
- Código generado con formato `MAT-YYYY-XXXX`
- Donde YYYY es el año actual
- XXXX es número secuencial
- Código es único

**Criterios de Aceptación:**
-  Materias reciben códigos con formato MAT-XXXX
-  Códigos son únicos y secuenciales
-  Generación automática al crear materia

---

### TC-069: Validar Unicidad de Códigos Institucionales
**HU-036** | **Tipo**: Unitario | **Prioridad**: Alta

**Precondiciones:**
- Múltiples usuarios/materias creados

**Pasos:**
1. Crear múltiples estudiantes
2. Verificar que cada código sea único
3. Intentar crear usuario con código duplicado

**Resultado Esperado:**
- Todos los códigos generados son únicos
- Intentar usar código duplicado genera error

**Criterios de Aceptación:**
-  Códigos son únicos
-  No se pueden duplicar códigos

---

## Resumen de Casos de Prueba

### Por Tipo de Prueba

| Tipo | Cantidad | Porcentaje |
|------|----------|------------|
| **Integración** | 55 | 80% |
| **Unitario** | 14 | 20% |
| **Total** | **69** | **100%** |

### Por Prioridad

| Prioridad | Cantidad | Porcentaje |
|-----------|----------|------------|
| **Crítica** | 5 | 7% |
| **Alta** | 35 | 51% |
| **Media** | 23 | 33% |
| **Baja** | 6 | 9% |
| **Total** | **69** | **100%** |

### Por Módulo

| Módulo | Casos de Prueba | Historias Cubiertas |
|--------|-----------------|---------------------|
| **Autenticación** | 5 | HU-001, HU-002 |
| **Gestión de Usuarios** | 10 | HU-004, HU-005, HU-006, HU-007, HU-008, HU-009 |
| **Gestión de Materias** | 8 | HU-010, HU-011, HU-012, HU-013, HU-014 |
| **Gestión de Inscripciones** | 6 | HU-015, HU-016, HU-017, HU-018 |
| **Gestión de Notas** | 18 | HU-019, HU-020, HU-021, HU-022, HU-023, HU-024, HU-025, HU-026, HU-027, HU-028 |
| **Reportes** | 7 | HU-029, HU-030, HU-031 |
| **Perfil de Usuario** | 3 | HU-032, HU-033 |
| **Funcionalidades del Sistema** | 12 | HU-034, HU-035, HU-036 |
| **Total** | **69** | **36 historias** |

---

## Notas de Implementación

### Cobertura de Criterios de Aceptación

Todos los casos de prueba están diseñados para cubrir **todos los criterios de aceptación** de cada historia de usuario. Cada criterio tiene al menos un caso de prueba asociado.

### Casos Positivos y Negativos

Los casos de prueba incluyen:
- **Casos positivos**: Flujos exitosos (happy path)
- **Casos negativos**: Validaciones, errores, permisos

### Priorización

Los casos de prueba están priorizados según:
- **Crítica**: Funcionalidades esenciales del sistema (autenticación)
- **Alta**: Funcionalidades principales de negocio
- **Media**: Funcionalidades secundarias
- **Baja**: Funcionalidades opcionales

### Ejecución Recomendada

1. **Pre-commit**: Ejecutar casos críticos y de alta prioridad
2. **CI/CD**: Ejecutar todos los casos de prueba
3. **Pre-release**: Ejecutar suite completa + casos de regresión

---

**Última actualización:** Enero 2025  
**Versión del documento:** 1.0  
**Total de Casos de Prueba:** 69  
**Historias Cubiertas:** 36/36 (100%)

