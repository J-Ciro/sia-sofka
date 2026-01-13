# Casos de Prueba en Formato Gherkin (BDD) - SIA SOFKA U

Este documento contiene todos los casos de prueba del sistema SIA SOFKA U convertidos al formato Gherkin para BDD (Behavior Driven Development).

**Formato:**
- **Feature**: Describe la funcionalidad
- **Scenario**: Describe un escenario de prueba
- **Given**: Precondiciones
- **When**: Acciones
- **Then**: Resultados esperados
- **And/But**: Para continuar con más pasos

---

## Feature: Autenticación

### Scenario: TC-001 - Login Exitoso con Credenciales Válidas
**HU-001** | **Tipo**: Integración | **Prioridad**: Crítica

```gherkin
Feature: Autenticación de Usuarios
  Como usuario del sistema
  Quiero iniciar sesión con mis credenciales
  Para acceder a las funcionalidades del sistema

  Scenario: Login exitoso con credenciales válidas
    Given que existe un usuario en el sistema con email "test@example.com" y contraseña "password123"
    And el usuario tiene un rol asignado "Admin"
    When realizo un POST a "/api/v1/auth/login" con:
      | username | test@example.com |
      | password | password123      |
    Then el sistema responde con status code 200
    And la respuesta contiene un campo "access_token"
    And la respuesta contiene un campo "token_type" con valor "bearer"
    And el token JWT incluye el campo "sub" con el email del usuario
    And el token JWT incluye el campo "role" con el rol del usuario
    And el token tiene tiempo de expiración configurado
```

### Scenario: TC-002 - Login Fallido con Email Incorrecto
**HU-001** | **Tipo**: Integración | **Prioridad**: Crítica

```gherkin
  Scenario: Login fallido con email incorrecto
    Given que no existe un usuario con el email "nonexistent@example.com"
    When realizo un POST a "/api/v1/auth/login" con:
      | username | nonexistent@example.com |
      | password | password123             |
    Then el sistema responde con status code 401
    And el mensaje de error es "Incorrect email or password"
```

### Scenario: TC-003 - Login Fallido con Contraseña Incorrecta
**HU-001** | **Tipo**: Integración | **Prioridad**: Crítica

```gherkin
  Scenario: Login fallido con contraseña incorrecta
    Given que existe un usuario en el sistema con email "test@example.com"
    When realizo un POST a "/api/v1/auth/login" con:
      | username | test@example.com |
      | password | wrongpassword    |
    Then el sistema responde con status code 401
    And el mensaje de error es "Incorrect email or password"
```

### Scenario: TC-004 - Validar Token JWT Incluye Rol
**HU-001** | **Tipo**: Unitario | **Prioridad**: Crítica

```gherkin
  Scenario: Validar que el token JWT incluye el rol del usuario
    Given que un usuario está autenticado
    And he recibido un token JWT
    When decodifico el token JWT
    Then el payload contiene el campo "sub" con el email
    And el payload contiene el campo "role" con el rol del usuario
    And el payload contiene el campo "exp" con la fecha de expiración
```

### Scenario: TC-005 - Validar Expiración del Token
**HU-001** | **Tipo**: Unitario | **Prioridad**: Media

```gherkin
  Scenario: Validar expiración del token JWT
    Given que se ha generado un token JWT con tiempo de expiración de 30 minutos
    When espero 30 minutos y 1 segundo
    And intento usar el token para acceder a un endpoint protegido
    Then el sistema responde con status code 401
    And el mensaje de error es "Could not validate credentials"
```

---

## Feature: Registro de Usuarios

### Scenario: TC-006 - Registrar Nuevo Usuario como Administrador
**HU-002** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
Feature: Registro de Usuarios
  Como administrador
  Quiero registrar nuevos usuarios (estudiantes o profesores)
  Para gestionar el sistema

  Scenario: Registrar nuevo usuario como administrador
    Given que estoy autenticado con rol "Admin"
    And tengo un token JWT válido
    When realizo un POST a "/api/v1/users" con:
      | email              | nuevo@example.com |
      | password           | password123       |
      | nombre             | Juan              |
      | apellido           | Pérez             |
      | fecha_nacimiento    | 2000-01-01        |
      | role               | Estudiante        |
      | programa_academico | Ingeniería        |
    Then el sistema responde con status code 201
    And la respuesta contiene los datos del usuario creado
    And el código institucional fue generado automáticamente
    And el email fue validado (no duplicado)
    And la edad fue calculada automáticamente
    And la contraseña fue almacenada como hash
```

### Scenario: TC-007 - Registrar Usuario con Email Duplicado
**HU-002** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Registrar usuario con email duplicado
    Given que estoy autenticado con rol "Admin"
    And existe un usuario con email "test@example.com"
    When realizo un POST a "/api/v1/users" con:
      | email    | test@example.com |
      | password | password123      |
      | nombre   | Juan             |
      | apellido | Pérez            |
      | role     | Estudiante       |
    Then el sistema responde con status code 400
    And el mensaje de error es "Email already registered"
```

### Scenario: TC-008 - Registrar Usuario sin Permisos de Admin
**HU-002** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Registrar usuario sin permisos de administrador
    Given que estoy autenticado con rol "Profesor"
    And tengo un token JWT válido
    When realizo un POST a "/api/v1/users" con datos de un nuevo usuario
    Then el sistema responde con status code 403
    And el mensaje de error es "Not enough permissions"
```

---

## Feature: Perfil de Usuario

### Scenario: TC-009 - Ver Información de Perfil Propio
**HU-003** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
Feature: Perfil de Usuario
  Como usuario autenticado
  Quiero ver mi información de perfil
  Para conocer mis datos personales

  Scenario: Ver información de perfil propio
    Given que estoy autenticado
    And tengo un token JWT válido
    When realizo un GET a "/api/v1/profile"
    And incluyo el header "Authorization: Bearer {token}"
    Then el sistema responde con status code 200
    And la respuesta contiene mi nombre
    And la respuesta contiene mi apellido
    And la respuesta contiene mi email
    And la respuesta contiene mi código institucional
    And la respuesta contiene mi rol
    And la respuesta contiene mi edad
    And solo se muestra información del usuario autenticado
```

---

## Feature: Gestión de Usuarios

### Scenario: TC-010 - Crear Estudiante como Administrador
**HU-004** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
Feature: Gestión de Usuarios
  Como administrador
  Quiero gestionar usuarios del sistema
  Para mantener actualizada la información

  Scenario: Crear estudiante como administrador
    Given que estoy autenticado con rol "Admin"
    When realizo un POST a "/api/v1/users" con:
      | email              | estudiante@example.com |
      | password           | password123            |
      | nombre             | María                 |
      | apellido           | García                 |
      | fecha_nacimiento    | 2000-05-15            |
      | role               | Estudiante             |
      | programa_academico | Medicina               |
      | ciudad_residencia  | Bogotá                 |
    Then el sistema responde con status code 201
    And el código institucional fue generado con formato "EST-XXXX"
    And el email fue validado (no duplicado)
    And la edad fue calculada automáticamente
    And el programa académico fue guardado
    And la ciudad de residencia fue guardada
```

### Scenario: TC-011 - Crear Profesor como Administrador
**HU-005** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Crear profesor como administrador
    Given que estoy autenticado con rol "Admin"
    When realizo un POST a "/api/v1/users" con:
      | email           | profesor@example.com |
      | password        | password123          |
      | nombre          | Carlos               |
      | apellido        | Rodríguez             |
      | fecha_nacimiento | 1980-03-20           |
      | role            | Profesor             |
      | area_ensenanza  | Matemáticas           |
    Then el sistema responde con status code 201
    And el código institucional fue generado con formato "PRO-XXXX"
    And el email fue validado (no duplicado)
    And la edad fue calculada automáticamente
    And el área de enseñanza fue guardada
```

### Scenario: TC-012 - Listar Todos los Usuarios como Administrador
**HU-006** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Listar todos los usuarios como administrador
    Given que estoy autenticado con rol "Admin"
    And existen múltiples usuarios creados (estudiantes y profesores)
    When realizo un GET a "/api/v1/users?skip=0&limit=10"
    And incluyo el header "Authorization: Bearer {token}"
    Then el sistema responde con status code 200
    And la lista contiene estudiantes y profesores
    And cada elemento muestra nombre, apellido, email, código institucional y rol
    And la paginación funciona correctamente (skip y limit)
```

### Scenario: TC-013 - Listar Usuarios sin Permisos de Admin
**HU-006** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Listar usuarios sin permisos de administrador
    Given que estoy autenticado con rol "Profesor"
    When realizo un GET a "/api/v1/users"
    And incluyo el header "Authorization: Bearer {token}" (no admin)
    Then el sistema responde con status code 403
    And el mensaje de error es "Not enough permissions"
```

### Scenario: TC-014 - Ver Detalles de un Usuario Específico
**HU-007** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Ver detalles de un usuario específico
    Given que estoy autenticado con rol "Admin"
    And existe un usuario con ID "1"
    When realizo un GET a "/api/v1/users/1"
    And incluyo el header "Authorization: Bearer {token}"
    Then el sistema responde con status code 200
    And la respuesta contiene toda la información del usuario
    And incluye nombre, apellido, email, código institucional, rol y edad
```

### Scenario: TC-015 - Ver Usuario Inexistente
**HU-007** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Ver usuario inexistente
    Given que estoy autenticado con rol "Admin"
    When realizo un GET a "/api/v1/users/99999"
    And incluyo el header "Authorization: Bearer {token}"
    Then el sistema responde con status code 404
    And el mensaje de error es "User with id 99999 not found"
```

### Scenario: TC-016 - Actualizar Usuario como Administrador
**HU-008** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Actualizar usuario como administrador
    Given que estoy autenticado con rol "Admin"
    And existe un usuario con ID "1"
    When realizo un PUT a "/api/v1/users/1" con:
      | nombre | Juan Actualizado |
    Then el sistema responde con status code 200
    And solo el campo "nombre" fue actualizado
    And el email no fue modificado
    And el código institucional no fue modificado
    And la respuesta contiene el usuario actualizado
```

### Scenario: TC-017 - Actualizar Usuario Inexistente
**HU-008** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Actualizar usuario inexistente
    Given que estoy autenticado con rol "Admin"
    When realizo un PUT a "/api/v1/users/99999" con datos de actualización
    Then el sistema responde con status code 404
    And el mensaje de error es "User with id 99999 not found"
```

### Scenario: TC-018 - Eliminar Usuario como Administrador
**HU-009** | **Tipo**: Integración | **Prioridad**: Baja

```gherkin
  Scenario: Eliminar usuario como administrador
    Given que estoy autenticado con rol "Admin"
    And existe un usuario con ID "1"
    When realizo un DELETE a "/api/v1/users/1"
    And incluyo el header "Authorization: Bearer {token}"
    Then el sistema responde con status code 204
    And el usuario fue eliminado de la base de datos
```

### Scenario: TC-019 - Eliminar Usuario Inexistente
**HU-009** | **Tipo**: Integración | **Prioridad**: Baja

```gherkin
  Scenario: Eliminar usuario inexistente
    Given que estoy autenticado con rol "Admin"
    When realizo un DELETE a "/api/v1/users/99999"
    Then el sistema responde con status code 404
    And el mensaje de error es "User with id 99999 not found"
```

---

## Feature: Gestión de Materias

### Scenario: TC-020 - Crear Materia como Administrador
**HU-010** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
Feature: Gestión de Materias
  Como administrador
  Quiero gestionar materias del sistema
  Para organizar el plan de estudios

  Scenario: Crear materia como administrador
    Given que estoy autenticado con rol "Admin"
    And existe un profesor con ID "1"
    When realizo un POST a "/api/v1/subjects" con:
      | nombre            | Matemáticas I      |
      | numero_creditos   | 3                  |
      | horario           | Lunes 8:00         |
      | descripcion       | Álgebra básica     |
      | profesor_id       | 1                  |
    Then el sistema responde con status code 201
    And el código institucional fue generado automáticamente con formato "MAT-XXXX"
    And el profesor fue asignado correctamente
    And todos los campos fueron guardados
```

### Scenario: TC-021 - Crear Materia con Profesor Inexistente
**HU-010** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Crear materia con profesor inexistente
    Given que estoy autenticado con rol "Admin"
    When realizo un POST a "/api/v1/subjects" con:
      | nombre      | Matemáticas I |
      | profesor_id | 99999         |
    Then el sistema responde con status code 404
    And el mensaje de error contiene "Profesor not found"
```

### Scenario: TC-022 - Crear Materia con Usuario que No es Profesor
**HU-010** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Crear materia con usuario que no es profesor
    Given que estoy autenticado con rol "Admin"
    And existe un estudiante con ID "1"
    When realizo un POST a "/api/v1/subjects" con:
      | nombre      | Matemáticas I |
      | profesor_id | 1             |
    Then el sistema responde con status code 400
    And el mensaje de error indica que el usuario debe ser de rol "PROFESOR"
```

### Scenario: TC-023 - Listar Todas las Materias como Administrador
**HU-011** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Listar todas las materias como administrador
    Given que estoy autenticado con rol "Admin"
    And existen múltiples materias creadas
    When realizo un GET a "/api/v1/subjects?skip=0&limit=10"
    Then el sistema responde con status code 200
    And la lista contiene todas las materias
    And cada materia incluye información del profesor asignado
    And la paginación funciona (skip y limit)
```

### Scenario: TC-024 - Ver Detalles de una Materia Específica
**HU-012** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Ver detalles de una materia específica
    Given que estoy autenticado con rol "Admin"
    And existe una materia con ID "1"
    When realizo un GET a "/api/v1/subjects/1"
    Then el sistema responde con status code 200
    And la respuesta contiene toda la información de la materia
    And incluye información del profesor asignado
```

### Scenario: TC-025 - Ver Materia Inexistente
**HU-012** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Ver materia inexistente
    Given que estoy autenticado con rol "Admin"
    When realizo un GET a "/api/v1/subjects/99999"
    Then el sistema responde con status code 404
    And el mensaje de error es "Subject with id 99999 not found"
```

### Scenario: TC-026 - Actualizar Materia como Administrador
**HU-013** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Actualizar materia como administrador
    Given que estoy autenticado con rol "Admin"
    And existe una materia con ID "1"
    And existe un profesor con ID "2"
    When realizo un PUT a "/api/v1/subjects/1" con:
      | nombre      | Matemáticas Avanzadas |
      | profesor_id | 2                    |
    Then el sistema responde con status code 200
    And solo los campos proporcionados fueron actualizados
    And el código institucional no fue modificado
    And el nuevo profesor fue validado (existe y es PROFESOR)
```

### Scenario: TC-027 - Eliminar Materia como Administrador
**HU-014** | **Tipo**: Integración | **Prioridad**: Baja

```gherkin
  Scenario: Eliminar materia como administrador
    Given que estoy autenticado con rol "Admin"
    And existe una materia con ID "1"
    When realizo un DELETE a "/api/v1/subjects/1"
    Then el sistema responde con status code 204
    And la materia fue eliminada de la base de datos
```

---

## Feature: Gestión de Inscripciones

### Scenario: TC-028 - Inscribir Estudiante a una Materia
**HU-015** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
Feature: Gestión de Inscripciones
  Como administrador
  Quiero gestionar las inscripciones de estudiantes a materias
  Para controlar la matrícula

  Scenario: Inscribir estudiante a una materia
    Given que estoy autenticado con rol "Admin"
    And existe un estudiante con ID "1"
    And existe una materia con ID "1"
    When realizo un POST a "/api/v1/enrollments" con:
      | estudiante_id | 1 |
      | subject_id    | 1 |
    Then el sistema responde con status code 201
    And la inscripción fue creada correctamente
    And el estudiante fue validado (existe y es ESTUDIANTE)
    And la materia fue validada (existe)
```

### Scenario: TC-029 - Inscribir Estudiante Duplicado en la Misma Materia
**HU-015** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Inscribir estudiante duplicado en la misma materia
    Given que estoy autenticado con rol "Admin"
    And existe una inscripción con estudiante_id "1" y subject_id "1"
    When realizo un POST a "/api/v1/enrollments" con:
      | estudiante_id | 1 |
      | subject_id    | 1 |
    Then el sistema responde con status code 409
    And el mensaje de error indica que la inscripción ya existe
```

### Scenario: TC-030 - Inscribir Usuario que No es Estudiante
**HU-015** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Inscribir usuario que no es estudiante
    Given que estoy autenticado con rol "Admin"
    And existe un profesor con ID "1"
    And existe una materia con ID "1"
    When realizo un POST a "/api/v1/enrollments" con:
      | estudiante_id | 1 |
      | subject_id    | 1 |
    Then el sistema responde con status code 400
    And el mensaje de error indica que el usuario debe ser "ESTUDIANTE"
```

### Scenario: TC-031 - Listar Todas las Inscripciones como Administrador
**HU-016** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Listar todas las inscripciones como administrador
    Given que estoy autenticado con rol "Admin"
    And existen múltiples inscripciones creadas
    When realizo un GET a "/api/v1/enrollments?skip=0&limit=10"
    Then el sistema responde con status code 200
    And la lista contiene todas las inscripciones
    And cada inscripción incluye ID, datos del estudiante, datos de la materia y fecha de creación
    And la paginación funciona
```

### Scenario: TC-032 - Ver Detalles de una Inscripción Específica
**HU-017** | **Tipo**: Integración | **Prioridad**: Baja

```gherkin
  Scenario: Ver detalles de una inscripción específica
    Given que estoy autenticado con rol "Admin"
    And existe una inscripción con ID "1"
    When realizo un GET a "/api/v1/enrollments/1"
    Then el sistema responde con status code 200
    And la respuesta contiene toda la información de la inscripción
    And incluye datos del estudiante y la materia
```

### Scenario: TC-033 - Eliminar Inscripción como Administrador
**HU-018** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Eliminar inscripción como administrador
    Given que estoy autenticado con rol "Admin"
    And existe una inscripción con ID "1"
    When realizo un DELETE a "/api/v1/enrollments/1"
    Then el sistema responde con status code 204
    And la inscripción fue eliminada de la base de datos
```

---

## Feature: Gestión de Notas

### Scenario: TC-034 - Crear Nota como Profesor en Materia Asignada
**HU-019** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
Feature: Gestión de Notas
  Como profesor
  Quiero gestionar las notas de mis estudiantes
  Para evaluar su desempeño

  Scenario: Crear nota como profesor en materia asignada
    Given que estoy autenticado con rol "Profesor"
    And tengo una materia asignada con ID "1"
    And existe un estudiante inscrito en la materia con enrollment_id "1"
    When realizo un POST a "/api/v1/grades" con:
      | enrollment_id | 1      |
      | nota          | 4.5    |
      | periodo       | 2024-1 |
      | fecha         | 2024-03-15 |
      | observaciones | Buen desempeño |
    Then el sistema responde con status code 201
    And la nota fue creada correctamente
    And el profesor fue validado (materia asignada)
    And el estudiante fue validado (inscrito en materia)
    And la nota está entre 0 y 5
```

### Scenario: TC-035 - Crear Nota como Profesor en Materia No Asignada
**HU-019** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Crear nota como profesor en materia no asignada
    Given que estoy autenticado con rol "Profesor"
    And NO tengo una materia asignada con ID "2"
    And existe una inscripción con enrollment_id "1"
    When intento crear una nota para la materia no asignada
    Then el sistema responde con status code 403
    And el mensaje de error es "Subject is not assigned to this profesor"
```

### Scenario: TC-036 - Crear Nota como Administrador
**HU-020** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Crear nota como administrador
    Given que estoy autenticado con rol "Admin"
    And existe una inscripción con enrollment_id "1"
    When realizo un POST a "/api/v1/grades" con datos de la nota
    Then el sistema responde con status code 201
    And la nota fue creada correctamente
    And el administrador puede crear para cualquier materia
    And el estudiante fue validado (inscrito)
```

### Scenario: TC-037 - Crear Nota con Valor Fuera de Rango
**HU-019, HU-020** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Crear nota con valor fuera de rango
    Given que estoy autenticado con rol "Profesor"
    And existe una inscripción con enrollment_id "1"
    When realizo un POST a "/api/v1/grades" con:
      | enrollment_id | 1   |
      | nota          | 6   |
      | periodo       | 2024-1 |
    Then el sistema responde con status code 422
    And el mensaje de validación indica que la nota debe estar entre 0 y 5
```

### Scenario: TC-038 - Ver Mis Notas como Estudiante
**HU-021** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Ver mis notas como estudiante
    Given que estoy autenticado con rol "Estudiante"
    And estoy inscrito en una materia con ID "1"
    And existen notas para mí en la materia
    When realizo un GET a "/api/v1/grades?subject_id=1"
    Then el sistema responde con status code 200
    And la lista contiene solo mis notas
    And cada nota incluye valor, período, fecha y observaciones
    And el estudiante fue validado (inscrito en materia)
```

### Scenario: TC-039 - Ver Notas como Estudiante No Inscrito
**HU-021** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Ver notas como estudiante no inscrito
    Given que estoy autenticado con rol "Estudiante"
    And NO estoy inscrito en la materia con ID "1"
    When realizo un GET a "/api/v1/grades?subject_id=1"
    Then el sistema responde con status code 403
    And el mensaje de error es "Estudiante not enrolled in subject"
```

### Scenario: TC-040 - Ver Notas de Materia como Profesor
**HU-022** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Ver notas de materia como profesor
    Given que estoy autenticado con rol "Profesor"
    And tengo una materia asignada con ID "1"
    And existen múltiples estudiantes con notas en la materia
    When realizo un GET a "/api/v1/grades?subject_id=1"
    Then el sistema responde con status code 200
    And la lista contiene todas las notas de la materia
    And cada nota incluye información del estudiante
    And el profesor fue validado (materia asignada)
```

### Scenario: TC-041 - Ver Notas de Materia No Asignada como Profesor
**HU-022** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Ver notas de materia no asignada como profesor
    Given que estoy autenticado con rol "Profesor"
    And NO tengo una materia asignada con ID "2"
    When realizo un GET a "/api/v1/grades?subject_id=2"
    Then el sistema responde con status code 403
    And el mensaje de error es "Subject is not assigned to this profesor"
```

### Scenario: TC-042 - Filtrar Notas por Enrollment ID como Profesor
**HU-022** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Filtrar notas por enrollment ID como profesor
    Given que estoy autenticado con rol "Profesor"
    And tengo una materia asignada con ID "1"
    And existe una inscripción con enrollment_id "1"
    When realizo un GET a "/api/v1/grades?enrollment_id=1"
    Then el sistema responde con status code 200
    And la lista contiene solo las notas de la inscripción especificada
    And el profesor fue validado (materia asignada)
```

### Scenario: TC-043 - Ver Todas las Notas como Administrador
**HU-023** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Ver todas las notas como administrador
    Given que estoy autenticado con rol "Admin"
    And existen múltiples notas en el sistema
    When realizo un GET a "/api/v1/grades"
    Then el sistema responde con status code 200
    And la lista contiene todas las notas del sistema
    And cada nota incluye información completa
```

### Scenario: TC-044 - Filtrar Notas por Materia como Administrador
**HU-023** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Filtrar notas por materia como administrador
    Given que estoy autenticado con rol "Admin"
    And existe una materia con ID "1" que tiene notas
    When realizo un GET a "/api/v1/grades?subject_id=1"
    Then el sistema responde con status code 200
    And la lista contiene solo las notas de la materia especificada
```

### Scenario: TC-045 - Ver Detalles de una Nota como Estudiante (Propia)
**HU-024** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Ver detalles de una nota como estudiante (propia)
    Given que estoy autenticado con rol "Estudiante"
    And existe una nota mía con ID "1"
    When realizo un GET a "/api/v1/grades/1"
    Then el sistema responde con status code 200
    And la respuesta contiene ID, nota, período, fecha, observaciones e información de inscripción
    And el estudiante fue validado (es mi propia nota)
```

### Scenario: TC-046 - Ver Detalles de Nota de Otro Estudiante
**HU-024** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Ver detalles de nota de otro estudiante
    Given que estoy autenticado con rol "Estudiante"
    And existe una nota de otro estudiante con ID "1"
    When realizo un GET a "/api/v1/grades/1"
    Then el sistema responde con status code 403
    And el mensaje de error es "Not enough permissions"
```

### Scenario: TC-047 - Ver Detalles de Nota como Profesor (Materia Asignada)
**HU-024** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Ver detalles de nota como profesor (materia asignada)
    Given que estoy autenticado con rol "Profesor"
    And existe una nota en una materia asignada con ID "1"
    When realizo un GET a "/api/v1/grades/1"
    Then el sistema responde con status code 200
    And la respuesta contiene información completa
    And el profesor fue validado (materia asignada)
```

### Scenario: TC-048 - Actualizar Nota como Profesor
**HU-025** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Actualizar nota como profesor
    Given que estoy autenticado con rol "Profesor"
    And existe una nota en una materia asignada con ID "1"
    When realizo un PUT a "/api/v1/grades/1" con:
      | nota | 4.8 |
    Then el sistema responde con status code 200
    And solo el campo "nota" fue actualizado
    And el profesor fue validado (materia asignada)
```

### Scenario: TC-049 - Actualizar Nota como Administrador
**HU-026** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Actualizar nota como administrador
    Given que estoy autenticado con rol "Admin"
    And existe una nota con ID "1"
    When realizo un PUT a "/api/v1/grades/1" con campos a actualizar
    Then el sistema responde con status code 200
    And el administrador puede actualizar cualquier nota
    And solo los campos proporcionados fueron actualizados
```

### Scenario: TC-050 - Eliminar Nota como Profesor
**HU-027** | **Tipo**: Integración | **Prioridad**: Baja

```gherkin
  Scenario: Eliminar nota como profesor
    Given que estoy autenticado con rol "Profesor"
    And existe una nota en una materia asignada con ID "1"
    When realizo un DELETE a "/api/v1/grades/1"
    Then el sistema responde con status code 204
    And la nota fue eliminada de la base de datos
    And el profesor fue validado (materia asignada)
```

### Scenario: TC-051 - Eliminar Nota como Administrador
**HU-028** | **Tipo**: Integración | **Prioridad**: Baja

```gherkin
  Scenario: Eliminar nota como administrador
    Given que estoy autenticado con rol "Admin"
    And existe una nota con ID "1"
    When realizo un DELETE a "/api/v1/grades/1"
    Then el sistema responde con status code 204
    And la nota fue eliminada de la base de datos
```

---

## Feature: Reportes

### Scenario: TC-052 - Generar Reporte de Estudiante en Formato PDF
**HU-029** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
Feature: Generación de Reportes
  Como administrador/profesor/estudiante
  Quiero generar reportes académicos
  Para analizar el desempeño

  Scenario: Generar reporte de estudiante en formato PDF
    Given que estoy autenticado con rol "Admin"
    And existe un estudiante con ID "1" que tiene notas en múltiples materias
    When realizo un GET a "/api/v1/reports/student/1?format=pdf"
    Then el sistema responde con status code 200
    And el Content-Type es "application/pdf"
    And el archivo PDF es descargable
    And el reporte incluye información del estudiante
    And el reporte incluye materias
    And el reporte incluye notas por materia
    And el reporte incluye promedio por materia
    And el reporte incluye promedio general ponderado
```

### Scenario: TC-053 - Generar Reporte de Estudiante en Formato HTML
**HU-029** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Generar reporte de estudiante en formato HTML
    Given que estoy autenticado con rol "Admin"
    And existe un estudiante con ID "1" que tiene notas
    When realizo un GET a "/api/v1/reports/student/1?format=html"
    Then el sistema responde con status code 200
    And el Content-Type es "text/html"
    And el archivo HTML es descargable
    And el reporte incluye información completa
```

### Scenario: TC-054 - Generar Reporte de Estudiante en Formato JSON
**HU-029** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Generar reporte de estudiante en formato JSON
    Given que estoy autenticado con rol "Admin"
    And existe un estudiante con ID "1" que tiene notas
    When realizo un GET a "/api/v1/reports/student/1?format=json"
    Then el sistema responde con status code 200
    And el Content-Type es "application/json"
    And la respuesta JSON tiene estructura completa del reporte
    And incluye información del estudiante, materias, notas y promedios
```

### Scenario: TC-055 - Generar Reporte de Materia como Profesor (PDF)
**HU-030** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Generar reporte de materia como profesor (PDF)
    Given que estoy autenticado con rol "Profesor"
    And tengo una materia asignada con ID "1"
    And existen múltiples estudiantes con notas en la materia
    When realizo un GET a "/api/v1/reports/subject/1?format=pdf"
    Then el sistema responde con status code 200
    And el Content-Type es "application/pdf"
    And el archivo PDF es descargable
    And el reporte incluye información de la materia
    And el reporte incluye lista de estudiantes
    And el reporte incluye notas de cada estudiante
    And el reporte incluye promedio de cada estudiante
    And el profesor fue validado (materia asignada)
```

### Scenario: TC-056 - Generar Reporte de Materia No Asignada como Profesor
**HU-030** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Generar reporte de materia no asignada como profesor
    Given que estoy autenticado con rol "Profesor"
    And NO tengo una materia asignada con ID "2"
    When realizo un GET a "/api/v1/reports/subject/2?format=pdf"
    Then el sistema responde con status code 403
    And el mensaje de error es "Subject is not assigned to this profesor"
```

### Scenario: TC-057 - Generar Reporte General como Estudiante (PDF)
**HU-031** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Generar reporte general como estudiante (PDF)
    Given que estoy autenticado con rol "Estudiante"
    And tengo notas en múltiples materias
    When realizo un GET a "/api/v1/reports/general?format=pdf"
    Then el sistema responde con status code 200
    And el Content-Type es "application/pdf"
    And el archivo PDF es descargable
    And el reporte incluye información del estudiante
    And el reporte incluye todas mis materias
    And el reporte incluye notas por materia
    And el reporte incluye promedio por materia
    And el reporte incluye promedio general ponderado
```

### Scenario: TC-058 - Generar Reporte General como Estudiante (JSON)
**HU-031** | **Tipo**: Integración | **Prioridad**: Alta

```gherkin
  Scenario: Generar reporte general como estudiante (JSON)
    Given que estoy autenticado con rol "Estudiante"
    And tengo notas
    When realizo un GET a "/api/v1/reports/general?format=json"
    Then el sistema responde con status code 200
    And el Content-Type es "application/json"
    And la respuesta JSON tiene estructura completa
    And incluye promedio general ponderado por créditos
```

---

## Feature: Actualización de Perfil

### Scenario: TC-059 - Ver Mi Perfil como Usuario Autenticado
**HU-032** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
Feature: Actualización de Perfil
  Como usuario autenticado
  Quiero ver y actualizar mi perfil
  Para mantener mi información actualizada

  Scenario: Ver mi perfil como usuario autenticado
    Given que estoy autenticado con cualquier rol
    And tengo un token JWT válido
    When realizo un GET a "/api/v1/profile"
    And incluyo el header "Authorization: Bearer {token}"
    Then el sistema responde con status code 200
    And la respuesta contiene mi nombre
    And la respuesta contiene mi apellido
    And la respuesta contiene mi email
    And la respuesta contiene mi código institucional
    And la respuesta contiene mi rol
    And la respuesta contiene mi edad
    And la respuesta contiene mi fecha de nacimiento
    And la respuesta contiene mi número de contacto
    And solo se muestra información del usuario autenticado
```

### Scenario: TC-060 - Actualizar Mi Perfil como Usuario Autenticado
**HU-033** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Actualizar mi perfil como usuario autenticado
    Given que estoy autenticado con cualquier rol
    When realizo un PUT a "/api/v1/profile" con:
      | nombre | Juan Actualizado |
    Then el sistema responde con status code 200
    And solo el campo "nombre" fue actualizado
    And el email no fue modificado
    And el código institucional no fue modificado
    And el rol no fue modificado
    And si se actualiza fecha de nacimiento, la edad se recalcula automáticamente
```

### Scenario: TC-061 - Intentar Cambiar Email en Perfil
**HU-033** | **Tipo**: Integración | **Prioridad**: Media

```gherkin
  Scenario: Intentar cambiar email en perfil
    Given que estoy autenticado
    When realizo un PUT a "/api/v1/profile" intentando enviar un email diferente
    Then el sistema responde con status code 400 o el campo se ignora
    And el email no fue actualizado
```

---

## Feature: Funcionalidades del Sistema

### Scenario: TC-062 - Cálculo Automático de Promedio por Materia
**HU-034** | **Tipo**: Unitario | **Prioridad**: Alta

```gherkin
Feature: Funcionalidades del Sistema
  Como sistema
  Quiero calcular promedios automáticamente
  Para facilitar la evaluación

  Scenario: Cálculo automático de promedio por materia
    Given que un estudiante está inscrito en una materia
    And existen múltiples notas registradas para el enrollment
    When obtengo todas las notas del enrollment
    And calculo el promedio
    Then el promedio se calcula como media aritmética de todas las notas
    And el resultado está redondeado a 2 decimales
    And si no hay notas, el promedio es None
```

### Scenario: TC-063 - Cálculo de Promedio con Notas Múltiples
**HU-034** | **Tipo**: Unitario | **Prioridad**: Alta

```gherkin
  Scenario: Cálculo de promedio con notas múltiples
    Given que un enrollment tiene 3 notas: 4.5, 3.8, 4.2
    When calculo el promedio
    Then el promedio es (4.5 + 3.8 + 4.2) / 3 = 4.17
    And está redondeado a 2 decimales
```

### Scenario: TC-064 - Cálculo Automático de Promedio General Ponderado
**HU-035** | **Tipo**: Unitario | **Prioridad**: Alta

```gherkin
  Scenario: Cálculo automático de promedio general ponderado
    Given que un estudiante tiene múltiples materias
    And cada materia tiene notas y créditos
    When obtengo todas las materias del estudiante con promedios
    And calculo el promedio general ponderado por créditos
    Then el promedio general es Σ(promedio_materia × créditos) / Σ(créditos)
    And solo se consideran materias con promedio calculado
    And el resultado está redondeado a 2 decimales
    And si no hay materias con notas, el promedio general es None
```

### Scenario: TC-065 - Cálculo de Promedio General con Múltiples Materias
**HU-035** | **Tipo**: Unitario | **Prioridad**: Alta

```gherkin
  Scenario: Cálculo de promedio general con múltiples materias
    Given que tengo:
      | Materia | Promedio | Créditos |
      | 1       | 4.5      | 3        |
      | 2       | 3.8      | 4        |
      | 3       | 4.2      | 2        |
    When calculo el promedio general ponderado
    Then el promedio es (4.5×3 + 3.8×4 + 4.2×2) / (3+4+2) = 4.12
    And está redondeado a 2 decimales
```

### Scenario: TC-066 - Generación Automática de Código Institucional para Estudiante
**HU-036** | **Tipo**: Unitario | **Prioridad**: Alta

```gherkin
  Scenario: Generación automática de código institucional para estudiante
    Given que la base de datos tiene estudiantes existentes
    When creo un nuevo estudiante sin código institucional
    Then el código fue generado con formato "EST-YYYY-XXXX"
    And YYYY es el año actual
    And XXXX es número secuencial
    And el código es único
```

### Scenario: TC-067 - Generación Automática de Código Institucional para Profesor
**HU-036** | **Tipo**: Unitario | **Prioridad**: Alta

```gherkin
  Scenario: Generación automática de código institucional para profesor
    Given que la base de datos tiene profesores existentes
    When creo un nuevo profesor sin código institucional
    Then el código fue generado con formato "PRO-YYYY-XXXX"
    And YYYY es el año actual
    And XXXX es número secuencial
    And el código es único
```

### Scenario: TC-068 - Generación Automática de Código Institucional para Materia
**HU-036** | **Tipo**: Unitario | **Prioridad**: Alta

```gherkin
  Scenario: Generación automática de código institucional para materia
    Given que la base de datos tiene materias existentes
    When creo una nueva materia sin código institucional
    Then el código fue generado con formato "MAT-YYYY-XXXX"
    And YYYY es el año actual
    And XXXX es número secuencial
    And el código es único
```

### Scenario: TC-069 - Validar Unicidad de Códigos Institucionales
**HU-036** | **Tipo**: Unitario | **Prioridad**: Alta

```gherkin
  Scenario: Validar unicidad de códigos institucionales
    Given que existen múltiples usuarios/materias creados
    When creo múltiples estudiantes
    Then cada código generado es único
    And cuando intento crear un usuario con código duplicado
    Then el sistema genera un error
```

---

## Resumen

### Estadísticas

- **Total de Features**: 8
- **Total de Scenarios**: 69
- **Historias Cubiertas**: 36/36 (100%)

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

---

**Última actualización:** Enero 2025  
**Versión del documento:** 1.0  
**Formato:** Gherkin (BDD)

